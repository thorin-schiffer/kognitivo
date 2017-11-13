package org.kognitivo.kognitivo;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.R.dimen;
import android.app.NotificationManager;
import android.app.Notification;
import android.app.PendingIntent;
import org.kivy.android.PythonActivity;
import android.graphics.Bitmap;
import android.graphics.drawable.BitmapDrawable;


public class Receiver extends BroadcastReceiver{

  final String LOG_TAG = "python";

  @Override
  public void onReceive(Context ctx, Intent intent) {
    Log.d(LOG_TAG, "Alarm service on receive...");
    NotificationManager notificationService = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
    Intent notificationIntent = new Intent(ctx, PythonActivity.class);
    notificationIntent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
    PendingIntent pendingIntent = (PendingIntent) PendingIntent.getActivity(ctx, 0, notificationIntent, 0);
    int iconResourceId = ctx.getResources().getIdentifier("icon", "drawable", ctx.getPackageName());
    Bitmap largeIcon = ((BitmapDrawable) ctx.getResources().getDrawable(iconResourceId)).getBitmap();

    float height = ctx.getResources().getDimension(dimen.notification_large_icon_height);
    float width = ctx.getResources().getDimension(dimen.notification_large_icon_width);
    largeIcon = Bitmap.createScaledBitmap(largeIcon, (int)width, (int)height, false);

    Notification notification = new Notification.Builder(ctx)
            .setContentTitle("Kognitivo")
            .setContentText(intent.getStringExtra("message"))
            .setSmallIcon(iconResourceId)
            .setLargeIcon(largeIcon)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build();
    notificationService.notify(0, notification);
  }
}