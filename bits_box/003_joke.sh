#!/bin/bash

# Bare minimum component example
#  * a <title> is required
#  * the file must be written to the ../_meta folder
#  * the script must be executable (chmod +x) to be picked up.

echo "<title>A joke</title>" > ../_meta/a_joke.html
echo "Q: What does a skeleton order at a restaurant?<br> " >> ../_meta/a_joke.html
echo "A: Spare ribs!" >> ../_meta/a_joke.html
echo " " >> ../_meta/a_joke.html
