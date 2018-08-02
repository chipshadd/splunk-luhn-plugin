#!/usr/bin/env python
'''
I created this because I wanted native search functionality to find possible credit card
numbers in my logs (or in given fields). The problem with relying on REGEX to do this
is that not all REGEX matches are actually credit card numbers.

This should be used as such:

	| luhn regex="<regex string>" output_field=<field_to_output_true/false> input_field=<field_to_check>

Defaults:

	regex = '(?:\d[ -]*?){13,30}'
		Note: This regex is used for initial matching of events. Matches are refined to have
			all non-numeric characters removed and are then checked again with...
				'(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})'

	input_field = _raw
	output_field = cc_luhn_check

How this works:

	1. Check to see if the provided field has regular expression matches using the intial
	match pattern (i.e. (?:\d[ -]*?){13,30}).

	2. Extract these matches, removing all non-numeric characters from each

	3. Check the created number with a more complex, credit card matching
	regular expression

	4. If there is a match, run a luhn check on the resulting number

'''

import re, sys
import splunk.Intersplunk as si

# Source: http://en.wikipedia.org/wiki/Luhn_algorithm
def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)

    for d in even_digits:
        checksum += sum(digits_of(d*2))

    return checksum % 10

import json

def cc_validity_check(card_number):
		with open("iin_table.json") as f:
			data = json.load(f)
		CC_LEN = len(card_number)
		VALID = 0
		i = 6
		while i <= 6 and i > 0:
			CC_PREFIX = str(card_number)[:i]
			try:
				if CC_LEN in data["IINs"][CC_PREFIX]["lengths"]:
					VALID = 1
					break
				else:
					break
			except:
				i -= 1
				continue
		return VALID

def is_luhn_valid(card_number):
	if luhn_checksum(card_number) == 0:
		return cc_validity_check(card_number) == 1
	else:
		return False

if __name__ == '__main__':
	try:
		default_pattern = '(?:\d[ -]*?){13,30}'
		'''
		Intersplunk: getKeywordsAndOptions()

		This returns a string array of the search terms used and a dictionary
		containing the key=value combinations of arguments passed to the command.
		Assuming the command were called as such:

			| luhn foo bar regex="\d+" output_field=tester input_field=_raw

		This call would return:
			keywords = [foo,bar]
			kvs = {
				"regex" : "\d+",
				"output_field" = "tester",
				"input_field" = "_raw"

			}
		'''
		keywords,options = si.getKeywordsAndOptions()

		'''
		pattern, output_field, input_field

		I want this command to have three optional parameters. The pattern is a regular
		expression pattern for matching events (before doing a luhn check) on the matched
		items.

		The input_field is the field to run the LUHN check on.

		The output_field is the field to dump results to (true/false).
		'''

		pattern = options.get('regex', None)
		if pattern == None:
			pattern = default_pattern

		output_field = options.get('output_field', None)
		if output_field == None:
			output_field = "cc_match_value"

		input_field = options.get('input_field', None)
		if input_field == None:
			input_field = "_raw"

		'''
		Compile the regular expression pattern for use with the re library
		'''
		try:
			initial_pattern = re.compile(pattern, re.M)
		except:
			# I'm doing this on the assumption that if a user gives a bad regex, it won't compile. This helps ensure stability.
			pattern = default_pattern
			initial_pattern = re.compile(default_pattern, re.M)

		cc_pattern = re.compile('(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})')

		'''
		Direct from Intersplunk.py:

	    Converts an Intersplunk-formatted file object into a dict
	    representation of the contained events, and returns a tuple of:

	        (results, dummyresults, settings)

	    "dummyresults" is always an empty list, and "settings" is always
	    an empty dict, since the change to csv stopped sending the
	    searchinfo.  It has not been updated to store the auth token.

		'''
		results,dummyresults,settings = si.getOrganizedResults()

		# I am going to modify the events to add a new field
		# this array will store the "new" events
		output_results = []

		# Loop through each result handed to this script
		for result in results:
			# We need to accommodate for the idea that the input field might be multivalue
			if type(result[input_field]) is list:
				test_value = ';;'.join(result[input_field])
			else:
				test_value = str(result[input_field])

			# First we do a regex match to find strings that might be
			# cc numbers
			matches = initial_pattern.findall(test_value)
			result["cc_luhn_initial_pattern"] = pattern

			if len(matches) == 0:
				result["cc_luhn_check"] = "false"
			else:
				# Loop through each match found; strip out all non-numeric characters;
				# take the resulting string and run it through a LUHN check
				# If it is validated by the LUHN check, return "true"
				result[output_field] = []
				for m in matches:
					mstr = str(''.join(c for c in m if c.isdigit()))
					if cc_pattern.match(mstr):
						if is_luhn_valid(mstr):
							result["cc_luhn_check"] = "true"
							result[output_field].append(m)

			# Append each line to our output array
			output_results.append(result)

		# Update the output; from Intersplunk.py
		'''
		    Outputs the contents of a result set to STDOUT in Interplunk
		    format, for consumption by the next search processor.
		'''
		si.outputResults(output_results)
	except Exception, e:
		import traceback
		stack =  traceback.format_exc()
		si.generateErrorResults("Error '%s'. %s" % (e, stack))

