# AngelInvesting
ssh root@194.164.151.204
root123@Angel..
localhost:8000

ssh akash@194.164.151.204 
akash123 
localhost:8001
sudo usermod -aG sudo akash

ssh yuvraj@194.164.151.204 
yuvraj123
localhost:8010

sudo adduser yuvraj
sudo usermod -aG sudo yuvraj

sudo su - yuvraj
mkdir -p ~/.ssh
chmod 700 ~/.ssh

username password
RMTestUser 9874563320
ACTestUser 7744110088
STTestUser 9966332255
UserTestRASM 9879879871

sudo chown -R akash:akash /var/www/AngelInvesting





<!-- =================================================================== -->
Thanks for the clear follow-up. This error:

❌ Failed to save 'index  2.html': Unable to write file (...) EACCES: permission denied

means that your user akash does not have write permissions to the file or its parent directory (/var/www/AngelInvesting/templates/admin/), even though you're in the sudo group.

This is a filesystem permissions issue, not a sudo issue.

✅ Solution: Change ownership or adjust permissions
To fix it, you have two main options:

Option 1: Change ownership to your user (akash)
Recommended if you're the main developer.

Run this as root or using sudo:




sudo chown -R akash:akash /var/www/AngelInvesting
This gives akash full ownership over everything in /var/www/AngelInvesting.

✅ Now you’ll be able to , create, and save files from VS Code over SSH.

Option 2: Give write permissions to your user/group (less preferred)
If you don’t want to change ownership, you can do:




sudo chmod -R u+rwX /var/www/AngelInvesting
Or, if you're in a shared environment and want to allow group write access:




sudo chgrp -R sudo /var/www/AngelInvesting
sudo chmod -R g+rwX /var/www/AngelInvesting
Be cautious: this might expose write access to other users in the sudo group.

🔍 Optional: Check current permissions
Before and after, you can inspect:




ls -la /var/www/AngelInvesting/templates/admin/
You'll likely see something like:

css


-rw-r--r-- 1 root root 1234 Jul 9  index  2.html
Which explains the permission denied — akash can’t write because root owns the file.

✅ Final Fix Command (most common case):



sudo chown -R akash:akash /var/www/AngelInvesting
Then go back to VS Code and try saving the file — it should now work without error.


sudo a2ensite angelinvesting.conf


Fixed Assets 10 8 43 38
CWIP 0 0 4 1.8
Investments 36 88 113 328
Trade Receivables 29 32 23 23
Inventory 0 0 0 0
Other Assets 856 748 658 855.2
Total Assets 931 876 841 1246
gap = 5
table header = user selects froom drop down (e.g. Fixed Assets 10 is selected as 2022 / FY 2022 -> next should ne automatically selected as  FY 2023,  FY 2024,  FY 2025  )



sudo chown -R www-data:www-data /var/www/AngelInvesting/media









ls -l /var/www/AngelInvesting/media/stock_logos/
sudo chmod -R 777 /var/www/AngelInvesting/media


source /var/www/AngelInvesting/venv/bin/activate

sudo systemctl restart gunicorn
sudo systemctl restart apache2

git add .
git commit -m "0"
git push origin branch24