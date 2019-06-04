#!/bin/bash

help () {
	echo "usage: timelapseBlur [option] [n]"
	echo "		option: n or pn"
	echo "			 n:	 creates an evenly weighted window n frames wide"
	echo "			pn:	 creates a window n+1 frames wide, weighted by binomial coefficients of power n"
	echo ""
	echo "		n: the value for the selected option"
	echo ""
	echo "		fps: frames per second for FFMPEG"
}

if [[ $1 == "" ]]; then
	echo "Error: Not enough inputs."
	help
	exit 1
else
	option=$1
fi

if [[ $2 == "" ]]; then
	echo "Error: Not enough inputs."
	help
	exit 1
else
	n=$2
fi

if [[ $3 == "" ]]; then
	echo "Error: Not enough inputs."
	help
	exit 1
else
	fps=$3
fi

flags="-monitor"

tempdir=temp
if [ ! -e "$tempdir" ]; then
	mkdir $tempdir
fi

declare -a filelist
filelist=(*.jpg)
N=${#filelist[@]}

if [[ $option == "pn" ]]; then
	tempname=p"$n"_temp
	output_convert=p"$n"_convert.mp4
	output_ffmpeg=p"$n"_"$fps"_ffmpeg.mp4
elif [[ $option == "n" ]]; then
	tempname="$n"_temp
	output_convert="$n"_convert.mp4
	output_ffmpeg="$n"_"$fps"_ffmpeg.mp4
fi

tempext=jpg

factorial () { 
    if (($1 == 1)) || (($1 == 0))
    then
        echo 1
        return
    else
        echo $(( $( factorial $(($1 - 1)) ) * $1 ))
    fi
}

combination () {
	local n=$1
	local k=$2
	if ((k>n)); then
		echo "Bad combination inputs: n:$n & k:$k" && exit;
	fi
	local nk
	local nf
	local kf
	local nkf
	local kfnkf
	#  / n \         n!
	# |     | =  ----------
	#  \ k /      k!(n-k)!
	let nk=n-k
	nf=$(factorial $n)
	kf=$(factorial $k)
	nkf=$(factorial $nk)
	let kfnkf=kf*nkf
	let C=nf/kfnkf
	echo $C
}

# 1st row pascal triangle

# nth row pascal triangle / binomial coefficients
# Top of triangle is 0th row
inputs_pn () {
	# requires input "n"
	local j
	local k
	inputs=""
	for ((j=0;j<=n;j++)); do
		C=$(combination $n $j)
		for ((k=0;k<C;k++)); do
			inputs="$inputs ${filelist[i+j]} "
		done
	done
}

inputs_n () {
	inputs=""
	for ((j=0;j<n;j++)); do
		inputs="$inputs ${filelist[i+j]}"
	done
}

case $option in
	pn )
		let N=N-n;
		input_func=inputs_pn;
		;;
	n )
		let N=N-n+1
		input_func=inputs_n;
		;;
esac

for ((i=0;i<N;i++)); do
	if [ ! -f $tempdir/$tempname$(printf "%03d" $i).$tempext ]; then
		$input_func
		convert $flags $inputs -average $tempdir/$tempname$(printf "%03d" $i).$tempext;
	fi
done

# convert $flags $tempdir/$tempname*.$tempext $output_convert;
if [ ! -f $output_ffmpeg ]; then
	ffmpeg -r $fps -i $tempdir/$tempname%3d.jpg -vcodec libx264 $output_ffmpeg
fi
