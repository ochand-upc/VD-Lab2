# Himalayan Expeditions Data Visualization - Product Requirements Document

## 1. Product Overview

### 1.1 Purpose
To develop an interactive multi-view data visualization system that provides insights into Himalayan expedition data, allowing users to explore patterns and relationships across routes, peaks, success rates, countries, and expedition characteristics.

### 1.2 Target Audience
Data analysts, researchers, mountaineering enthusiasts, and users interested in analyzing patterns in Himalayan expeditions.

## 2. Objectives

### 2.1 Primary Goal
Create a connected multi-view visualization system that enables comprehensive analysis of Himalayan expedition data through interactive components.

### 2.2 Key Questions to Answer
1. Which routes have the highest and lowest success rates for different peaks?
2. Which countries have led the most expeditions for different periods of time?
3. Do longer expeditions have a higher chance of summiting successfully for each peak? Does this change per season?
4. How have termination reasons evolved over the years for each peak?

## 3. Data Requirements

### 3.1 Data Sources
- Primary dataset: Himalayan expeditions dataset (input_data/exped_tidy.csv, input_data/peaks_tidy.csv)
- Supplementary data: Geographic information (input_data/unique_peaks_coords.csv)

### 3.2 Data Processing
- Clean and filter the dataset to remove inconsistencies, missing values, and irrelevant information
- Maintain data integrity to ensure all questions can be answered while removing problematic data
- Augment the dataset with additional information as needed
- Document all data cleaning and processing steps thoroughly (max 300 words)
- Steps should be reproducible, allowing transformation from raw to cleaned data
- Processing tools: Python Pandas

## 4. Functional Requirements

### 4.1 Visualization Requirements
- A chart for answearing each question need to be designed and implemented
- All visualizations must be created using Vega-Altair
- Implement connected multi-view visualizations to enable coordinated exploration
- Include interactive elements that facilitate question answering
- Ensure readability, usability, and accessibility (color blindness considerations)
- Maintain color consistency across visualizations (same color = same meaning)
- Include appropriate titles, labels, and annotations

### 4.2 Interaction Requirements
- Design meaningful interactions that reduce the number of steps needed to answer questions
- Implement filtering, selection, and highlighting capabilities
- Ensure default configuration states are meaningful
- Minimize the number of interactions required to solve each problem

### 4.3 Platform Requirements
- Google Colab: Implement and document visualization designs and data processing
- Streamlit: Develop the final interactive application with all visualizations

## 5. Design Requirements

### 5.1 Design Process Documentation
- For each question (visualization), document (max 300 words per question):
  * Chart selection and reasoning
  * Interactivity selection and reasoning
  * Design iterations and changes
  * Readability and usability improvements
  * Alternative designs considered

### 5.2 Multi-View Design
- Document the overall multi-view system design process (max 500 words)
- Include a step-by-step guide on how to solve each task
- Explain improvements made for consistency, aesthetics, and usability

### 5.3 Layout Considerations
- All questions should be solvable on a single page with minimal scrolling
- Limit vertical scrolling to at most twice the height of a 15" laptop screen
- Use both vertical and horizontal alignments to facilitate comparisons
- Group related visualizations together, separate unrelated ones
- Use space efficiently and effectively

## 6. Implementation Requirements

### 6.1 Tools and Technologies
- Data Processing: Python Pandas
- Visualization: Vega-Altair
- Application Development: Streamlit
- Documentation: Google Colab notebook

### 6.2 Performance Considerations
- Filter data appropriately before visualization to optimize performance
- Ensure the application runs smoothly on standard hardware

## 7. Deliverables

### 7.1 Required Components
- Cleaned dataset files
- Google Colab notebook (.ipynb) containing:
  * Author's name
  * Code for visualizations
  * Explanations and documentation
  * Design process documentation
- Streamlit application code (.py) implementing all visualizations
- A single ZIP file containing all components above, named after the author

### 7.2 Documentation Requirements
- Data cleaning process (max 300 words)
- Design process for each question (max 300 words each)
- Overall multi-view system design (max 500 words)
- Step-by-step instructions for solving each task

## 8. Evaluation Criteria

### 8.1 Grading Factors
- Number of variables included in visualizations
- Number of non-trivial tasks effectively addressed
- Integration of additional data sources
- Thoroughness of documentation
- Design quality and iterative improvements
- Usability and functionality of the final application

## 9. Timeline

### 9.1 Deadline
- Final submission: June 2nd

## 10. Checklist for Submission

### 10.1 General Requirements
- [ ] Name the file after the author
- [ ] Include author's name as the first line in the notebook
- [ ] Include cleaned data
- [ ] Compress all files in a single ZIP file (no RAR or other formats)
- [ ] Include author's name in notebook and Streamlit app
- [ ] Ensure data file names match those referenced in code
- [ ] Ensure data is properly cleaned
- [ ] Verify code executes without errors
- [ ] Include step-by-step design process documentation

### 10.2 Visualization Requirements
- [ ] Use only Vega-Altair for all visualizations
- [ ] Consider color blindness in design
- [ ] Ensure color consistency across visualizations
- [ ] Include meaningful titles, labels, and annotations
- [ ] Check visibility of elements with varying opacity
- [ ] Consider data normalization where appropriate

### 10.3 Streamlit Application Requirements
- [ ] Ensure all questions are answerable on a single page
- [ ] Verify application runs with "streamlit run <application_name>"
- [ ] Include a comprehensive final visualization
- [ ] Maintain alignment and consistency
- [ ] Use space effectively
- [ ] Maximize the number of variables and questions addressed
- [ ] Filter unused data before visualization
- [ ] Set meaningful default values for selections
- [ ] Minimize required interactions to solve problems