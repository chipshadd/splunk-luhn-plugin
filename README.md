The splunk lunh checker (found here: https://splunkbase.splunk.com/app/2753/#/overview) is a plugin to detect any credit card numbers being shipped in logs.  From my experience with it, it returned a lot of false positivesfrom strings of digits found in logs that coincidentally passes luhn validation.

I altered it to include an additional check to verify if the number it thinks is a credit card matches a valid length given the IIN prefix (first 6 digits).
Table of IINs and lengths I used found here: https://en.wikipedia.org/wiki/Payment_card_number

How to use:

Install the lunh app as you would any other splunk app, then drop the iin_table.json file into the same directory as the lunh.py script (<splunk_base_directory>/etc/apps/ta_luhn/bin): and replace the lunh.py script there with this one.

I've create a bash script to generate the iin_table.json file in case you need to remove or add an IIN.
