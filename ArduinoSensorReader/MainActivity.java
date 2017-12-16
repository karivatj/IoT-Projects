package sokeri.arduino.gassensorreader;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Timer;
import java.util.TimerTask;
import java.util.UUID;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends ActionBarActivity
{
    private TextView txtADC0 = null;
    private TextView txtADC1 = null;
    private TextView txtADC2 = null;
    private Button btnRetry = null;
    private int adc0_value = 0;
    private int adc1_value = 0;
    private int adc2_value = 0;

    private static final String TAG = "Gas Reader";
    private BluetoothAdapter m_btAdapter = null;
    private BluetoothSocket m_btSocket = null;
    private BluetoothDevice m_btDevice = null;
    private InputStream m_inputStream = null;
    private OutputStream m_outputStream = null;

    private static final UUID SPP_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"); //SPP UUID used for serial port communication

    private boolean connected = false;
    private boolean connecting = false;
    private boolean btWasDisabled = false;

    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

        Log.d(TAG, "onCreate()");

        setContentView(R.layout.activity_main);

        txtADC0 = (TextView) findViewById(R.id.textADC0);
        txtADC1 = (TextView) findViewById(R.id.textADC1);
        txtADC2 = (TextView) findViewById(R.id.textADC2);

        btnRetry = (Button) findViewById(R.id.btnRetry);

        btnRetry.setOnClickListener(new View.OnClickListener()
        {
            public void onClick(View v)
            {
                if(!m_btAdapter.isEnabled())
                {
                    showToast("Please turn on Bluetooth before connecting!");
                    return;
                }
                if(!connected && !connecting)
                {
                    btnRetry.setEnabled(false);
                    showToast("Connecting to Arduino");
                    new ConnectToArduino().execute();
                }
            }
        });

        //Reset possible connections before proceeding
        resetConnection();
    }

    @Override
    public void onResume()
    {
        super.onResume();

        Log.d(TAG, "onResume()");

        m_btAdapter = BluetoothAdapter.getDefaultAdapter();

        //Emulator does not have bluetooth
        if (m_btAdapter == null)
        {
            Log.d(TAG, "Could not get Bluetooth instance. Check connection settings!");
            finish();
        }
        else
        {
            if (!m_btAdapter.isEnabled())
            {
                btWasDisabled = true;
                m_btAdapter.enable(); //Not recommended. You should always ask for permission to turn on BT but in this exercise lets just do it this way
                Log.d(TAG, "Bluetooth activated");
            }
        }
    }

    @Override
    public void onPause()
    {
        super.onPause();

        Log.d(TAG, "onPause()");

        resetConnection();

        btnRetry.setEnabled(true);

        //Turn off Bluetooth before leaving
        if (m_btAdapter.isEnabled() && btWasDisabled)
        {
            m_btAdapter.disable();
            Log.d(TAG, "Bluetooth disabled");
        }
    }

    private void showToast(String msg)
    {
        Toast toast = Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_SHORT);
        toast.show();
    }

    private void updateSensorData()
    {
        txtADC0.setText(Integer.toString(adc0_value));
        txtADC1.setText(Integer.toString(adc1_value));
        txtADC2.setText(Integer.toString(adc2_value));
    }

    private void receive()
    {
        //Every 1000 ms
        Timer timer = new Timer();
        timer.scheduleAtFixedRate( new TimerTask()
        {
            public void run()
            {
                try
                {
                    new SocketOperation().execute();
                }
                catch (Exception e) {}

            }
        }, 0, 1000);
    }

    private void resetConnection()
    {
        if (m_inputStream != null) {
            try {
                m_inputStream.close();
            } catch (Exception ignored) {
            }
            m_inputStream = null;
        }

        if (m_outputStream != null) {
            try {
                m_outputStream.close();
            } catch (Exception ignored) {
            }
            m_outputStream = null;
        }

        if (m_btSocket != null) {
            try {
                m_btSocket.close();
            } catch (Exception ignored) {
            }
            m_btSocket = null;
        }

        connected = false;
        connecting = false;
        Log.d(TAG, "Connection reset");
    }

    private void send(String message)
    {
        Log.d(TAG, "Sending data: " + message);

        try {
            m_outputStream.write(message.getBytes());
        } catch (IOException e) {
            Log.d(TAG, "Exception raised while sending data: " + e.getMessage());
        }
    }

    private class ConnectToArduino extends AsyncTask<String, Void, String>
    {

        @Override
        protected String doInBackground(String... params)
        {
            connecting = true;
            Log.d(TAG, "Setting up connection");

            if (m_btDevice == null)
                m_btDevice = m_btAdapter.getRemoteDevice("20:14:04:11:35:11");  //Arduino HC-06 MAC-address

            try {
                m_btSocket = m_btDevice.createRfcommSocketToServiceRecord(SPP_UUID);
            } catch (IOException e) {
                return "Socket Creation Error";
            }

            Log.d(TAG, "Trying to connect");

            try {
                m_btSocket.connect();
            } catch (IOException e) {
                Log.d(TAG, "Exception raised during connect: " + e.getMessage());
                return "Connection Error";
            }

            try {
                m_outputStream = m_btSocket.getOutputStream();
                m_inputStream = m_btSocket.getInputStream();
            } catch (IOException e) {
                Log.d(TAG, "Error while attaching I/O streams to socket: " + e.getMessage());
                return "IO Stream Exception";
            }

            connected = true;
            return "Connected";
        }

        @Override
        protected void onPostExecute(String result)
        {
            Log.d(TAG, "Connection result: " + result);

            if(connected)
            {
                showToast("Connected");
                btnRetry.setEnabled(false);
                receive();
            }
            else
            {
                showToast("Connection Failure");
                btnRetry.setEnabled(true);
            }

            connecting = false;
        }

        @Override
        protected void onPreExecute() {}

        @Override
        protected void onProgressUpdate(Void... values) {}
    }

    private class SocketOperation extends AsyncTask<String, Void, String> {

        @Override
        protected String doInBackground(String... params)
        {
            String result = null;

            if(connected)
            {
                try {
                    int bytesAvailable = m_inputStream.available();

                    if (bytesAvailable > 0)
                    {
                        byte[] bytes = new byte[1024];
                        int readbytes = m_inputStream.read(bytes);

                        result = new String(bytes, "UTF-8").substring(0, readbytes);
                    }
                } catch (IOException ignored) { }
            }

            return result;
        }

        @Override
        protected void onPostExecute(String result)
        {
            if(result != null && result.contains(";")) //If the message contains a semicolon we know that it is data we are interested in
            {
                result = result.replace("\n", "").replace("\r", ""); //Remove newlines and linebreaks
                Log.d(TAG, result);
                String[] parts = result.split(";");

                adc0_value = Integer.parseInt(parts[0]);
                adc1_value = Integer.parseInt(parts[1]);
                adc2_value = Integer.parseInt(parts[2]);
            }

            updateSensorData();
        }

        @Override
        protected void onPreExecute() {}

        @Override
        protected void onProgressUpdate(Void... values) {}
    }
}