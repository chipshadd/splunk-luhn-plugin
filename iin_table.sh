#!/bin/bash
#Credit card info based on the IIN table found here: https://en.wikipedia.org/wiki/Payment_card_number
OUT="iin_table.json"
function insert {
	NAME=$1; shift
	LUNH=$1; shift
	LEN=$1; shift
	PRE=$@
	for i in $PRE; do
		cat <<EOF >>$OUT
		"$i": {
			"name": "$NAME",
			"lunh": $LUNH,
			"lengths": [ $LEN ]
		},
EOF
	done
}

function insert_last {
	NAME=$1; shift
	LUNH=$1; shift
	LEN=$1; shift
	PRE=$@
	for i in $PRE; do
		cat <<EOF >>$OUT
		"$i": {
			"name": "$NAME",
			"lunh": $LUNH,
			"lengths": [ $LEN ]
		}
EOF
	done
}

cat <<EOF > $OUT
{
	"IINs": { 
EOF

#Usage: insert <name> <lunh t/f> <cc lengths> <IIN ranges>
insert "American Express" "true" "15" "34 37"
insert "Bankcard" "true" "16" "5610 `seq 560221 560225`"
insert "China UnionPay" "true" "16, 17, 18, 19" "62"
insert "Diners Club enRoute" "false" "15" "2014 2149"
insert "Diners Club International" "true" "14, 15, 16, 17, 18, 19" "36"
insert "Diners Club International" "true" "16, 17, 18, 19" "`seq 300 305` 3095 38 39"
insert "Diners Club United States & Canada" "true" "16" "54 55"
insert "Discover Card" "true" "16, 17, 18, 19" "6011 64 65"
insert "RuPay" "true" "16" "60 6521"
insert "InterPayment" "true" "16, 17, 18, 19" "636"
insert "InstaPayment" "true" "16" "`seq 637 639`"
insert "JCB" "true" "16, 17, 18, 19" "`seq 3528 3589`"
insert "Laser" "true" "16, 17, 18, 19" "6304 6706 6771 6709"
insert "Maestro" "true" "12, 13, 14, 15, 16, 17, 18, 19" "50 `seq 56 58` 639 67"
insert "Dankort" "true" "16" "5019 4571"
insert "MIR" "true" "16" "`seq 2200 2204`"
insert "MasterCard" "true" "16" "`seq 2221 2720` `seq 51 55`"
insert "Troy" "true" "16" "`seq 979200 979289`"
insert "Visa" "true" "16" "4"
insert "UATP" "true" "15" "1"
insert "Verve" "true" "16, 19" "`seq 506099 506198` `seq 650002 650026`"
insert_last "Verve" "true" "16, 19" "650027"

cat <<EOF >>$OUT
	}
}
EOF
