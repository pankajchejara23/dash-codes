from ReAudio import ReAudio

f = ReAudio('Tobias_meeting.csv')
degrees= f.getHighestFourDegrees(plot=False)
print(degrees)
f.assignUserLabel()
f.drawNetwork()
