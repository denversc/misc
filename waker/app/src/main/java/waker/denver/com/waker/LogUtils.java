package waker.denver.com.waker;

import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.util.Log;

/**
 * Methods that make logging to Android Logcat a little easier in the application.
 */
public class LogUtils {

    /**
     * The "tag" that is specified to the log methods.
     */
    private static final String LOG_TAG = "Waker";

    /**
     * Private constructor to prevent instantiation.
     */
    private LogUtils() {
    }

    public static void logD(@NonNull String tag, @Nullable String message) {
        if (!BuildConfig.DEBUG) {
            // this method should be stripped by ProGuard anyways
            // but we abort just to be safe
            return;
        }
        final String logMessage = createLogMessage(tag, message);
        Log.d(LOG_TAG, logMessage);
    }

    public static void logV(@NonNull String tag, @Nullable String message) {
        if (!BuildConfig.DEBUG) {
            // this method should be stripped by ProGuard anyways
            // but we abort just to be safe
            return;
        }
        final String logMessage = createLogMessage(tag, message);
        Log.v(LOG_TAG, logMessage);
    }

    public static void logI(@NonNull String tag, @Nullable String message) {
        final String logMessage = createLogMessage(tag, message);
        Log.i(LOG_TAG, logMessage);
    }

    public static void logW(@NonNull String tag, @Nullable String message) {
        final String logMessage = createLogMessage(tag, message);
        Log.w(LOG_TAG, logMessage);
    }

    public static void logW(@NonNull String tag, @Nullable String message, @Nullable Throwable tr) {
        final String logMessage = createLogMessage(tag, message);
        Log.w(LOG_TAG, logMessage, tr);
    }

    public static void logE(@NonNull String tag, @Nullable String message) {
        final String logMessage = createLogMessage(tag, message);
        Log.e(LOG_TAG, logMessage);
    }

    public static void logE(@NonNull String tag, @Nullable String message, @Nullable Throwable tr) {
        final String logMessage = createLogMessage(tag, message);
        Log.e(LOG_TAG, logMessage, tr);
    }

    @NonNull
    private static String createLogMessage(@NonNull String tag, @Nullable String message) {
        return tag + ": " + message;
    }

}
