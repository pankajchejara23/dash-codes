from ReAudio_group import ReAudio

re = ReAudio('group_audio.csv')

#print(re.getSpeakingTime(plot=False,group='group-1'))
re.drawNetwork('group-2')
