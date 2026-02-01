# Image Sorter

A tool designed to automatically categorize images and videos based on their aspect ratios into logical folders like 16X9, 4X3, or 1X1.

## Features

* Uses Farey Sequence to match approximate resolutions.
* Uses both PIL and hachoir.

## Usage
```
python image_sorter.py [directory] [limiter] [--move]
```

## Examples
> python image_sorter.py ./Photos 25

> python image_sorter.py ./Downloads --move
