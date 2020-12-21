# Alteryx SDK CSV Append
Custom Alteryx tool to append data to CSV files

Custom Alteryx SDK tool that allows you to append data to an existing CSV file. Output confuguration largely matches standard Alteryx outputs with Code Page, Line Ending Style and delimiter.

The tool will not create files, if you want to do this just use the standard Alteryx output to CSV tool.

Headers will also not be added to the ouput since this tool expects a file has alreayd been created with headers if required.

__Note that the output file name does not need to be .csv, it will work with any flat file format incluing files without a file extension (Unix, Mac type files)__

## Installation
Download the yxi file and double click to install in Alteyrx. 

<img src="https://github.com/bobpeers/Alteryx_SDK_CSVAppend/blob/main/images/csvinstall.png" alt="CSV Append Install Dialog">

The tool will be installed in the __In/Out__ category.

<img src="https://github.com/bobpeers/Alteryx_SDK_CSVAppend/blob/main/images/CSVAppend_toolbar.png" alt="CSV Append Install Toolbar">

## Requirements

None, uses standard Python libraries.

## Usage
Configure the tool as you would any standard output tool.

## Outputs
The tool has no output.

## Usage
This workflow demonstrates the tool in use. The workflow shown here:

<img src="https://github.com/bobpeers/Alteryx_SDK_CSVAppend/blob/main/images/CSVAppend_workflow.png" width="1000" alt="CSV Append Workflow">
