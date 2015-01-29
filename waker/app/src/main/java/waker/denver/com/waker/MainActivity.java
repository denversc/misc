package waker.denver.com.waker;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.view.View;
import android.widget.CheckBox;

import static waker.denver.com.waker.LogUtils.logD;

public class MainActivity extends Activity {

    private static final String LOG_TAG = "MainActivity";

    private CheckBox mCheckBox;
    private ServiceConnection mServiceConnection;
    private WakerService.Controller mController;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        logD(LOG_TAG, "onCreate()");
        super.onCreate(savedInstanceState);
        mServiceConnection = new ServiceConnectionImpl();

        setContentView(R.layout.activity_main);
        mCheckBox = (CheckBox) findViewById(R.id.chk_keep_awake);
        mCheckBox.setOnClickListener(new KeepAwakeCheckboxOnClickListener());
    }

    @Override
    protected void onDestroy() {
        logD(LOG_TAG, "onDestroy()");
        super.onDestroy();
        mServiceConnection = null;
    }

    @Override
    protected void onResume() {
        logD(LOG_TAG, "onResume()");
        super.onResume();

        mCheckBox.setEnabled(false);
        final Intent intent = new Intent();
        intent.setClass(this, WakerService.class);
        bindService(intent, mServiceConnection, BIND_AUTO_CREATE);
    }

    @Override
    protected void onPause() {
        logD(LOG_TAG, "onPause()");
        try {
            mCheckBox.setEnabled(false);
            unbindService(mServiceConnection);
        } finally {
            super.onPause();
        }
    }

    private class ServiceConnectionImpl implements ServiceConnection {

        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            logD(LOG_TAG, "onServiceConnected() name=" + name + " service=" + service);
            mController = (WakerService.Controller) service;
            mController.isKeepingAwake(new IsKeepingAwakeBooleanResultCallback());
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            logD(LOG_TAG, "onServiceDisconnected() name=" + name);
            mController = null;
            mCheckBox.setEnabled(false);
        }

    }

    private class IsKeepingAwakeBooleanResultCallback implements BooleanResultCallback {

        @Override
        public void setResult(boolean isKeepingAwake) {
            logD(LOG_TAG, "IsKeepingAwakeBooleanResultCallback isKeepingAwake=" + isKeepingAwake);
            mCheckBox.setChecked(isKeepingAwake);
            mCheckBox.setEnabled(true);
        }

    }

    private class KeepAwakeCheckboxOnClickListener implements View.OnClickListener {

        @Override
        public void onClick(View view) {
            final CheckBox checkBox = (CheckBox) view;
            final boolean keepAwake = checkBox.isChecked();
            logD(LOG_TAG, "KeepAwakeCheckbox clicked; keepAwake=" + keepAwake);

            final WakerService.Controller controller = mController;
            if (controller != null) {
                controller.setKeepAwake(keepAwake);
            }
        }

    }
}
