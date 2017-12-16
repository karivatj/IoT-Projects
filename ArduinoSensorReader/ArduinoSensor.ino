/*
 * Simple gas sensor implementation for Arduino Nano.
 * This implementation is able to read analog inputs from
 * attached gas sensors through inputs A0 - A2.
 * Makes a conversion every second and outputs the values
 * over Bluetooth to a supported handheld device.
 *
 * @author Kari Vatjus-Anttila (kari.vatjusanttila@gmail.com)
 *
 * References:
 * http://appelsiini.net/2011/simple-usart-with-avr-libc
 * http://www.ermicro.com/blog/?p=325
 * http://atmega32-avr.com/atmega328-datasheet/
 * http://www.nongnu.org/avr-libc/user-manual/group__avr__stdio.html
 */

#include <stdio.h>

/*Defines for Serial bus communication. F_CPU and BAUD has to be defined before including setbaud.h*/
#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#ifndef BAUD
#define BAUD 9600
#endif
#include <util/setbaud.h>

/*Configure I/O Streams*/
FILE serialOutput;
FILE serialInput;

volatile int adc0 = 0;
volatile int adc1 = 0;
volatile int adc2 = 0;
volatile int sensorValue = 0;
volatile int currentChannel = 0;

void setup()
{
    fdev_setup_stream(&serialOutput, serialWrite, NULL, _FDEV_SETUP_WRITE);
    fdev_setup_stream(&serialInput, NULL, serialRead, _FDEV_SETUP_READ);

    SREG  &= ~(1 << 7);                             //Disable interrupts
    DDRB  = (1 << 5);                               //Enable LED
    DDRC  = DDRC | B01111000;                       //Analog pins 0 and 1 as output

    /*Setup timer 1 and corresponding interrupts*/
    TCCR1A &= ~((1 << WGM11) | (1 << WGM10));       //Clear WGM11 and WGM10 fields from TCCR1A
    TCCR1B  =   (1 << WGM12);                       //Set WGM12
    TCCR1B &=  ~(1 << WGM13);                       //Clear WGM13. Result: WGM13 = 0, WGM12 = 1, WGM11 = 0, WGM10 = 0 -> 0100 -> CTC Mode
    TIMSK1 |=   (1 << OCIE1A);                      //Trigger interrupt when the timer and OCR1A registers match
    OCR1AH = B00111101;                             //High byte = 3d. Timer compare register high byte
    OCR1AL = B00001001;                             //Low byte = 09.Timer compare register low byte. 3d09 = 15625
    TCCR1B |= (1 << CS12) | (1 << CS10);            //Start the timer at clock interval (16 Mhz / 1024) Hz ~ Once per second

    /*Setup ADC and corresponding interrupts*/
    DIDR0  = B00111111;                             // From the datasheet: When an analog signal is applied these bits should be written to one to reduce power consumption.
    ADMUX  = B01000000;                             // Measure on ADC0 and set reference voltage.
    ADCSRA = B10011111;                             // AD-converter enabled. Interrupt enabled, Prescaler 128
    ADCSRA |= 1 << ADSC;                            // Start Conversion

    /*Configure Serial bus*/
    UBRR0H = UBRRH_VALUE;                           //Baudrate register 0 High-byte. UBRR(H/L)_VALUE contains the (upper/lower) byte of the calculated prescaler value
    UBRR0L = UBRRL_VALUE;                           //Baudrate register 0 Low-byte

    #if USE_2X                                      //USE_2X defines if UART has to be configured to run in double speed.
        UCSR0A |= _BV(U2X0);                        //UCSR0A register contains mainly status data. _BV is a helper macro for bit setting
    #else
        UCSR0A &= ~(_BV(U2X0));
    #endif

    /*UCSR0B/C registers contain the configuration data for UART*/
    UCSR0C = _BV(UCSZ01) | _BV(UCSZ00);             // 8-bit data
    UCSR0B = _BV(RXEN0)  | _BV(TXEN0);              // Enable RX and TX

    /*Set stdio to use our own methods*/
    stdout = &serialOutput;
    stdin  = &serialInput;

    SREG |= (1 << 7);                               //Enable interrupts
}

void loop()
{
    char buffer[50];

    sprintf (buffer, "%d;%d;%d", adc0, adc1, adc2);

    puts(buffer);

    delay(1000);
}

/*Utility function to write to the serial bus*/
int serialWrite(char c, FILE *stream)
{
    //If a newline is detected. Append a carriage return to the message aswell
    if (c == '\n')
        serialWrite('\r', stream);

    //Wait until the transmit buffer is able to receive more data
    loop_until_bit_is_set(UCSR0A, UDRE0);
    UDR0 = c;
}

/*Utility function to read from the serial bus*/
int serialRead(FILE *stream)
{
    loop_until_bit_is_set(UCSR0A, RXC0);  //Wait until theres new data to be received
    return UDR0;
}

/*ADC Conversion Ready Interrupt*/
ISR(ADC_vect)
{
    sensorValue = ADCL;        //Store low byte from ADC
    sensorValue += ADCH << 8;  //Store high byte from ADC
}

/*Timer1 Interrupt*/
ISR(TIMER1_COMPA_vect)
{
    PORTB ^= (1 << 5);  //Blink LED to indicate that Timer Interrupt occured.

    switch(currentChannel)
    {
        case 0:
          adc0 = sensorValue;
          ADMUX  = B01000001; // Measure next on ADC1 and set reference voltage.
          break;
        case 1:
          adc1 = sensorValue;
          ADMUX  = B01000010; // Measure next on ADC2 and set reference voltage.
          break;
        case 2:
          adc2 = sensorValue;
          ADMUX  = B01000000; // Measure next on ADC0 and set reference voltage.
          break;
        default:
          break;
    }

    currentChannel++;

    if(currentChannel % 3 == 0)
      currentChannel = 0;

    ADCSRA |= 1 << ADSC;  //Trigger a new conversion
}
