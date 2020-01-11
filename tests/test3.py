from PELETools.ControlFileParser import ControlFileBuilder

cf_builder = ControlFileBuilder('data/adaptive.conf')
cf = cf_builder.build()

sim = cf.getSimulation()

list_of_reports = []
for epoch in sim:
    for report in epoch:
        list_of_reports.append(report)

for report in list_of_reports:
    print(report, str(report.epoch))

current_report = list_of_reports[0]
print('Working with report \'{}\''.format(current_report))

n_steps = current_report.getMetric(2)

print(' Is trajectory parsed?')
print(current_report.trajectory.is_parsed)

print('Parsing trajectories')
sim.parse_trajectories(n_processors=2)

print(' Is trajectory parsed?')
print(current_report.trajectory.is_parsed)

current_report.trajectory.parsed_data.xyz
