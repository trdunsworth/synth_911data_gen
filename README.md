# Synthetic 911 Data Generator

 Synthetic Data Generator for 911 call center data

This is a generator to create synthetic data for presentation purposes.
I give presentations on using statistics in 911 centers. However, I do not want to expose actual 911 calls to the public. This generator will create synthetic data that can be used in place of actual data.

## File List

synth911gen.py is designed to emulate 9-1-1 call list data for a primary PSAP that dispatches for police, fire, and EMS units. The code can be altered to create a generator for only specific agencies, or agencies can be added, for example, if you need separate calls for animal control or community intervention teams, etc.

synthvolgen.py is designed to emulate 9-1-1 call center volumes, including abandoned calls and outbound calls. If a center answers 10-digit emergency lines, the code can be extended to allow for those volumes as well. The final two columns, pct_15 and pct_20, are included as the percentage of 911 calls answered in 15 or 20 seconds to comport with the NFPA and NENA guidelines of 90% answered in 15 seconds and 95% answered in 20 seconds. A user could also alter the percentages in the code to reflect different performances for the imaginary center.

faker_911_problems is a work in progress. I am creating a dynamic provider for the faker library to add problem natures to the computer_aided_dispatch.csv that is generated by synth911gen.py. The skeletal code is in place, and I have a.csv file of problem types from a PSAP. All of the types will not be used in the file when updated.

## TODO

1. finish creating the faker provider and look at submitting a version of it as a contribution to the faker library
2. add the custom dynamic provider into synth911gen.py
3. improve the documentation surrounding this project
4. add code for 10-digit emergency lines into synthvolgen.py *I will leave it commented out at this time*
5. add code for pct_10 and pct_40 *Leave Commented Out in the base*
6. tie the priority level to the problem nature and remove the random generator for priority
7. add additional elapsed time breakpoints as needed *2025-03-30: Added ack_time as a breakpoint for the time between first dispatch and first marked enroute*
8. create additional parameter hooks for running the code to give additional customization options.
9. see if faker.bothify can generate id numbers using the pattern '24-######')
10. determine if I can switch from np.random_gaussian or np.random_exponential to a Poisson distribution of values.
11. Create and add a GUI interface for easier data generation.

If anyone has additional suggestions or ideas, email me at [Dr. D](mailto:drddatascience@gmail.com)
