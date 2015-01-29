package waker.denver.com.waker;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.PowerManager;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;

import static waker.denver.com.waker.LogUtils.logD;

/**
 * Waker service.
 */
public class WakerService extends Service {

    private static final String LOG_TAG = "WakerService";

    private static final String ACTION_SET_KEEP_AWAKE = "set_keep_awake";
    private static final String EXTRA_AWAKE = "awake";

    private PowerManager.WakeLock mWakeLock;

    private final Object mHandlerLock;
    private Handler mHandler;

    public WakerService() {
        mHandlerLock = new Object();
    }

    @Override
    public IBinder onBind(Intent intent) {
        logD(LOG_TAG, "onBind() intent=" + intent);
        return new ControllerImpl();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        logD(LOG_TAG, "onStartCommand() intent=" + intent + " flags=" + flags + " startId=" + startId);

        final String action = intent.getAction();
        if (ACTION_SET_KEEP_AWAKE.equals(action)) {
            final boolean awake = intent.getBooleanExtra(EXTRA_AWAKE, false);
            if (awake) {
                logD(LOG_TAG, action + " mWakeLock.acquire()");
                mWakeLock.acquire();
            } else {
                logD(LOG_TAG, action + " mWakeLock.release()");
                mWakeLock.release();
                stopSelf(startId);
            }
        }

        return START_STICKY;
    }

    @Override
    public void onCreate() {
        logD(LOG_TAG, "onCreate()");
        super.onCreate();

        synchronized (mHandlerLock) {
            mHandler = new Handler(new HandlerCallbackImpl());
        }

        final Object service = getSystemService(POWER_SERVICE);
        final PowerManager pm = (PowerManager) service;
        mWakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "WakerService");
        mWakeLock.setReferenceCounted(false);
    }

    @Override
    public void onDestroy() {
        logD(LOG_TAG, "onDestroy()");
        try {
            final PowerManager.WakeLock wakeLock = mWakeLock;
            mWakeLock = null;

            synchronized (mHandlerLock) {
                mHandler = null;
            }

            if (wakeLock != null) {
                wakeLock.release();
            }
        } finally {
            super.onDestroy();
        }
    }

    private boolean isKeepingAwake() {
        final boolean isKeepingAwake;
        if (mWakeLock == null) {
            isKeepingAwake = false;
        } else {
            isKeepingAwake = mWakeLock.isHeld();
        }
        logD(LOG_TAG, "isKeepingAwake() returns " + isKeepingAwake);
        return isKeepingAwake;
    }

    private void setKeepAwake(boolean value) {
        logD(LOG_TAG, "setKeepAwake() " + value);
        final Intent intent = new Intent();
        intent.setClass(this, WakerService.class);
        intent.setAction(ACTION_SET_KEEP_AWAKE);
        intent.putExtra(EXTRA_AWAKE, value);
        startService(intent);
    }

    public static interface Controller {

        public void isKeepingAwake(@NonNull BooleanResultCallback callback);

        public void setKeepAwake(boolean value);

    }

    private class ControllerImpl extends Binder implements Controller {

        @Override
        public void isKeepingAwake(@NonNull BooleanResultCallback callback) {
            logD(LOG_TAG, "isKeepingAwake() callback=" + callback);
            sendMessage(HandlerCallbackImpl.MSG_IS_KEEPING_AWAKEED, callback);
        }

        @Override
        public void setKeepAwake(boolean value) {
            logD(LOG_TAG, "setKeepingAwake() " + value);
            final int arg1 = value ? 1 : 0;
            sendMessage(HandlerCallbackImpl.MSG_SET_KEEP_AWAKEED, arg1);
        }

        private void sendMessage(int what, @Nullable Object obj) {
            sendMessage(what, 0, obj);
        }

        private void sendMessage(int what, int arg1) {
            sendMessage(what, arg1, null);
        }

        private void sendMessage(int what, int arg1, @Nullable Object obj) {
            synchronized (mHandlerLock) {
                if (mHandler == null) {
                    return;
                }
                final Message message = mHandler.obtainMessage();
                message.what = what;
                message.arg1 = arg1;
                message.obj = obj;
                message.sendToTarget();
            }
        }

    }

    private class HandlerCallbackImpl implements Handler.Callback {

        public static final int MSG_IS_KEEPING_AWAKEED = 1;
        public static final int MSG_SET_KEEP_AWAKEED = 2;

        @Override
        public boolean handleMessage(Message msg) {
            switch (msg.what) {
                case MSG_IS_KEEPING_AWAKEED: {
                    final BooleanResultCallback callback = (BooleanResultCallback) msg.obj;
                    final boolean isKeepingAwake = isKeepingAwake();
                    callback.setResult(isKeepingAwake);
                    return true;
                }
                case MSG_SET_KEEP_AWAKEED: {
                    final boolean value = (msg.arg1 == 1) ? true : false;
                    return true;
                }
                default:
                    return false;
            }
        }

    }

}
