# Microsoft Your Phone Restore

Restore cached messages form Microsoft Your Phone to your Android device.

I lost all my phone messages due to the data partition corrupting, and wanted to get what out what was stored by the Windows You Phone app.

This python 3 program will convert the Your Phone db into an xml that can be restored with [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore)

# Current Status

SMS works well, but MMS are not fully working.

# How to use

Rename `phoneNumber.properties.example` to `phoneNumber.properties` and put your phone number in there with formatting and country code.

Copy the `phone.db` file from `C:\Users\[USER NAME]\AppData\Local\Packages\Microsoft.YourPhone_8wekyb3d8bbwe\LocalCache\Indexed\[RANDOM NUMBER]\System\Database` to the folder.

Run `python convert.py`

Take the xml file from output and copy it to your phone.

Restore it with [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore)
