# Ugglor
Repository containing code to analyze sounds of European owls. 
The scripts here are based on the [BirdNET-Analyzer](https://github.com/BirdNET-Team/BirdNET-Analyzer) software and use data from [xeno-canto](https://xeno-canto.org/).

The following scripts are available:

+ fetch-xeno-canto.py - will fetch information for user defined species from xeno-canto and, if requested, download sound files as well.

+ eagle-owl-sex.py - will read a bunch of sound files, measure the peak frequency (highest volume) and based on that guess the sex of the owl. It will also produce plots of the peak frequencies for individuals classified as male and female.

