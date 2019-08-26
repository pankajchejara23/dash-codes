"""
Log_Speech_Analyzer: This class contains function to process Etherpad Logs (obtained by ep_update_track plugin) and ReSpeaker audio data of direction of arrival.

Author: Pankaj Chejara
Email: pankajch@tlu.ee


"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
from collections import Counter
import networkx as nx
import sys

class Log_Speech_Analyzer(object):

    """
    init function initialize the Log_Speech_Analyzer object.
    it takes two parameters, Etherpad log file name and Speech file name.
    """
    def __init__(self, log_file=None,speech_file=None):
        self.log_file_name = log_file
        self.speech_file_name = speech_file
        self.ip_list={}
        print("-------------Etherpad logs and Microphone speech Analyzer -------------")
        print("Loading.......")
        try:
            # Reading log and speech csv data files
            if log_file:
                self.log_file = pd.read_csv(log_file,names=['timestamp','ip','action','oldlen','newlen','changeset','charbank','noadd','noremove'])
                print('Log file is loaded successfully....')
                # Setting timestamp as index for both dataframes
                self.log_file = self.log_file.set_index(pd.DatetimeIndex(self.log_file['timestamp']))
            if speech_file:
                self.speech_file = pd.read_csv(speech_file,names=['timestamp','direction'])
                print('Speech file is loaded successfully....')
                self.speech_file = self.speech_file.set_index(pd.DatetimeIndex(self.speech_file['timestamp']))

        except Exception as e:
            print('Error occured while opening the file',e)


    """
    plotDoaDistribution: This function plot the distribution of DoA (Direaction of Arrival).

    """

    def plotDoaDistribution(self):
        self.degree_frequency = Counter(self.speech_file['direction'])
        plt.bar(self.degree_frequency.keys(),self.degree_frequency.values(),width=10)
        plt.xlabel('Direction of arrival')
        plt.ylabel('Frequency')
        plt.title('Frequncy distribution of DoA (Direction of Arrival)')
        plt.show()



    """
    getHighestFourDegrees: This function will search through the speech file and extract four degrees corresponding to users.
                           It simply count the degree frequency and return four degrees with highest frequencies.

    Return: A list of highest four degrees
    """
    def getHighestFourDegrees(self):
        try:

            # If file is not in required format then break
            if len(self.speech_file.columns) != 2:
                print('File has more than two columns. File must have two columns (timestamp,degree)')
                return null


            # Count the frequency of each degree in the file
            self.degree_frequency = Counter(self.speech_file['direction'])

            # Sort the degrees on the basis of their counted frequency
            sorted_deg_freq = sorted(self.degree_frequency.items(),key=lambda x:x[1])

            # Return first six high frequecy directions
            highest_degrees = sorted_deg_freq[-6:]


            # Sort the order of highest degrees
            highest_degrees = sorted(highest_degrees,key=lambda x:x[0])

            # list to store final four directions
            high_four_degrees = []

            # Iterate over six direactions of highest frequency

            for item in highest_degrees:

                if len(high_four_degrees)==0:
                    high_four_degrees.append(item[0])
                else:
                    if abs(item[0]-high_four_degrees[-1])%360 > 40:

                        high_four_degrees.append(item[0])
                    else:
                        if item[1]>self.degree_frequency[high_four_degrees[-1]]:
                            high_four_degrees.remove(high_four_degrees[-1])
                            high_four_degrees.append(item[0])
                        else:
                            pass




            return high_four_degrees
        except Exception as e:
            print('Exception:',sys.exc_info())




    """
    assignUserLabel: This function assigns the user identifier (1,2,3,4) on the basis of direction of arrival of sound.
                     This function assumes that participants are sitting clockwise around ReSpeaker and first participant sitting at zero degree.

                     For orientation specification, please see this picture


    """
    def assignUserLabel(self):
        # Get four highly occuring direction of arrival
        highDegrees = self.getHighestFourDegrees()

        # Considering degrees in ascending order corresponds to user1 to user4
        users = np.array([item for item in highDegrees])


        # This function takes the degree and assign label on the basis of its closeness to high occuring degrees
        def assign_label(degree):

            # Computer the absolute difference between four highly occuring degree and the argument
            user_diff = np.absolute(users-degree)

            # Identifying the minimum difference
            min_diff = np.min(user_diff)


            # Getting the indices of minimum element
            indices = np.where(user_diff==min_diff)

            # Getting the first index (np.where() returns a list, therefore we need to select the first element)
            # Also np.where() returns indices (which starts from 0, whereas user identifier starts from 1.). We addedd 1 to the index to get the user identifier
            ind = indices[0]+1

            # Return the user identifier correpsonds to degree (parameter)
            return ind[0]

        # Add one column to the pandas dataframe with name 'users' which contains corresponding user identifier
        self.speech_file['users'] = self.speech_file['direction'].map(assign_label)



    """
    getTotalSpeakingTime: This function computes the total speaking time for each user

    Arguments:
        plot: Boolean argument, Specify True if you want to plot the bar graph of speaking time
        time: string, Possible values ('sec','min','hour') time unit
    """
    def getSpeakingTime(self,plot,time='sec'):


        self.assignUserLabel()

        # Count the frequency for each user
        speech_count = self.speech_file.groupby('users').count()

        # Create a dictionary for storing speaking time for each user and initialize it with zero
        user_speak_time = {1:0,2:0,3:0,4:0}

        # Iterate for each user
        for i in range(4):

            # If time unit is sec then multiply the frequency with 200/1000. As each entry represent user speaking behavior on scale of 200 ms.
            # To convert it into second, we need to multiply the frequency count for specific user with 200/1000
            if time=='sec':
                user_speak_time[i+1] = speech_count.loc[i+1,'direction']*float(200/1000)

            # Same as above but for time unit minute
            elif time=='min':
                user_speak_time[i+1] = speech_count.loc[i+1,'direction']*float(200/(60*1000))

            # For time unit hour
            elif time=='hour':
                user_speak_time[i+1] = speech_count.loc[i+1,'direction']*float(200/(60*60*1000))


        # Plot the speaking time for each user (if plot==True in the parameters)
        if plot:
            plt.figure()
            plt.bar(user_speak_time.keys(),user_speak_time.values())
            plt.ylabel('Time(%s)' % time)
            plt.xlabel('Users')
            plt.xticks(np.arange(4)+1,['user-1','user-2','user-3','user-4'])
            plt.title('Total speaking time for each user')
            plt.show()
        return user_speak_time



    """
    generateEdgeFile: This function generates a file containing the edge in the form of (i,j) where i and j represents users i and user j.
                      If a user a speaks after user b then it will be considered an edge (b,a)

    """
    def generateEdgeFile(self,seq=[]):

        # Check if this function called after calling assignUserLabel() function.
        # if yes then access the users column and convert it into numpy array for further processing

        if len(seq)==0:
            self.assignUserLabel()
            sequence = self.speech_file['users'].to_numpy()
        else:
            sequence = seq
        # Create a emplty data frame with column users and conti_frequency. Here, conti_frequency represents the continuous occurence of particular user.
        # For instance, if a user speaks then there will be many entries for that particular user because one entry recorded for every 200 ms.
        # We are considering if atleast 4 entries are found continuous then it will be treated as speaking activity.
        df = pd.DataFrame(columns=['users','conti_frequency'])


        # This function will count the number of continuous occurence
        def count_conti_occurence(index):

            # Set count to 0
            count=0

            # Starts from the given index
            j = index

            # Loop to iterate over the users sequence
            while j<len(sequence):

                # Increase the count if the element at given index (parameter) is same as the iterated element
                if sequence[j] == sequence[index]:
                    count +=1

                # If mismatch found, break the loop
                else:
                    break

                # Increases j
                j +=1

            # Return number of count for sequence[index] and index of first next occurence of different element.
            return count,(j-index)

        # Set i to 0 for the Loop
        i = 0

        # Iterate for entire sequence of users
        while i < len(sequence):

            # Call count_conti_occurence() function
            count,diff = count_conti_occurence(i)


            # Add continuous frequency of current user (sequence[i]) to the dataframe
            df = df.append({'users':sequence[i],'conti_frequency':count},ignore_index=True)

            # Move to next different element
            i = i + diff

        # We are considering speaking activtiy if there are 3 consecutive entries for one particular user
        process_df = df.where(df.conti_frequency>2)

        # Deleting other users with less than 3 consecutive entries
        process_df.dropna(axis=0,how='any',inplace=True)

        # Resultant sequence to generate edge file
        processed_sequence = process_df['users'].to_numpy()

        # Open a file to write the edges
        file  = open('edges.txt','w')

        # Create an empty list
        edge_list = list()

        # Create two variable node1 and node2 and set them to zero.
        node1=node2=0

        # Iterate over resultant users sequences
        for i in range(len(processed_sequence)):

            # For the first element
            if node1==0:
                # set node1 to the first element
                node1=processed_sequence[i]

            # For rest of the elements
            else:

                # Set the current element to node2
                node2=processed_sequence[i]

                if node2 != node1:
                    # Append the edge node1, node2 to the edge list
                    edge_list.append((node1,node2))

                    # Print the edge
                    print("{},{}".format(node1,node2))

                    # Write the edge in the file
                    file.write("{},{}\n".format(node1,node2))

                # Set the node1 as node2
                node1=node2

        return edge_list
        # Close the file
        file.close()

        # Print the message
        print('Edge file is generated with name edges.txt')


    def drawNetwork(self,speak_time,edge_list):




        # Get speaking time for each user
        sp_beh = speak_time

        # Compute average speaking time
        sp_avg = sum(sp_beh.values())/float(len(sp_beh.values()))

        # Create an empty graph using networkx library
        G = nx.Graph()

        # Iterate over edge list
        for edge in edge_list:

        # Check if the current edge already exist or not
            if G.has_edge(edge[0],edge[1]):

                # Get the weight of that edge
                w = G[edge[0]][edge[1]]['weight']

                # Remove it from the graph
                G.remove_edge(edge[0],edge[1])

                # Add it again with updated weight
                G.add_edge(edge[0],edge[1],weight=w+.5)

            else:

                # If edge doesn't exist in the graph then add it with weight .5
                G.add_edge(edge[0],edge[1],weight=.5)

        # Layout for showing the network
        pos = nx.spring_layout(G)

        # Get the edges from the graph
        edges = G.edges()

        # Get the weight for every edge
        weights = [G[u][v]['weight'] for u,v in edges]

        # Generate the colormap for the each node on the basis of their speaking time
        color_map = []

        # iterate for each node in the graph
        for node in G:

            # Assign red color if speaking time is below average
            if sp_beh[node]<sp_avg-1:
                color_map.append('red')
            # Assign plum color if speaking time is near average
            elif sp_beh[node]<sp_avg+1 and sp_beh[node]>sp_avg-1:
                color_map.append('plum')

            # Assign green for above average
            else:
                color_map.append('lawngreen')

        # Draw the network
        nx.draw(G, pos,node_color=color_map,  edges=edges,width=weights,with_labels=True)








    """
    plotEtherpadStat: This function plot the overall stats for Etherpad for every specified time window.
    """

    def plotEtherpadStat(self,plot,timescale='30S'):
        self.log_file['addition'] = self.log_file['newlen']-self.log_file['oldlen']
        self.log_file['deletion'] = self.log_file['oldlen']-self.log_file['newlen']
        mask = self.log_file['addition']<0
        mask2 = self.log_file['deletion']<0
        self.log_file.loc[mask,'addition']=0
        self.log_file.loc[mask2,'deletion']=0
        stat = self.log_file.groupby(pd.Grouper(freq=timescale)).sum()

        if plot:
            print('plotting...')
            stat[['addition','deletion']].plot(kind='bar')
            plt.title('Overall Stats for Etherpad')
            plt.show()


    """
    mergeLogSpeech: This function combines Etherpad Log data with Speech data.
    @param
        ip_list: This is a list of IP addresses belongs to Users. Ip addresses must be specified in the order of user1, user2, user3, user4
        window_size: It will take specified window size (in seconds) to merge data from both files. By default it takes 30 Seconds.
        file_name: You can specify the name for the final merged file.

    """

    def mergeLogSpeech(self,ip_list=['192.168.1.235','192.168.1.193','',''],window_size='30S',write_file=False):


        df1 = self.log_file
        df2 = self.speech_file
        if 'users' not in df2.columns:
            self.assignUserLabel()
        if 'addition' not in df1.columns:
            self.plotEtherpadStat(plot=False)
        df1['timestamp'] = pd.to_datetime(df1['timestamp'])
        df2['timestamp'] = pd.to_datetime(df2['timestamp'])
        if 'timestamp' in df1.columns:
            if 'timestamp' in df2.columns:
                print ("Timestamp column found in both dataframes")
                df1 = df1.set_index(pd.DatetimeIndex(df1['timestamp']))
                df2 = df2.set_index(pd.DatetimeIndex(df2['timestamp']))

                if df1.timestamp[0] > df2.timestamp[0]:
                    start = df1
                else:
                    start = df2

                if df1.timestamp[df1.shape[0]-1] > df2.timestamp[df2.shape[0]-1]:
                    last = df1
                else:
                    last = df2


                cur_ts = start.timestamp[0]
                #print('Type:',type(cur_ts))
                time_delta = pd.to_timedelta(window_size)
                final = pd.DataFrame(columns=['timestamp','u1_add','u1_del','u1_text','u2_add','u2_del','u2_text','u3_add','u3_del','u3_text','u4_add','u4_del','u4_text','u1_speak','u2_speak','u3_speak','u4_speak','speak_sequence'])
                while cur_ts < last.timestamp[last.shape[0]-1]:

                    next_ts = cur_ts + time_delta
                    print ('Start:',cur_ts,' End:',next_ts)
                    temp_log_df = df1.between_time(datetime.datetime.time(cur_ts),datetime.datetime.time(next_ts),include_start=True,include_end=False)
                    temp_speech_df = df2.between_time(datetime.datetime.time(cur_ts),datetime.datetime.time(next_ts),include_start=True,include_end=False)

                    entry = self.extractFeatures(cur_ts,temp_log_df,temp_speech_df,ip_list)
                    #print(entry)
                    #final = final.append({'timestamp':entry['timestamp'],'u1_add':entry['u1_add'],'u1_del':entry['u1_del'],'u1_text':entry['u1_text'],'u2_add':entry['u2_add'],'u2_del':entry['u2_del'],'u2_text':entry['u2_text'],'u3_add':entry['u3_add'],'u3_del':entry['u3_del'],'u3_text':entry['u3_text'],'u4_add':entry['u4_add'],'u4_del':entry['u4_del'],'u4_text':entry['u4_text'],'u1_speak':entry['u1_speak'],'u2_speak':entry['u2_speak'],'u3_speak':entry['u3_speak'],'u4_speak':entry['u4_speak'],'speak_sequence':entry['speak_sequence']},ignore_index=True)
                    final = final.append(entry,ignore_index=True)

                    cur_ts = next_ts
                if write_file:
                    final.to_csv('Final_combined.csv',index=False)
                    print("Merged data have been written in Final.csv file")
                else:
                    return final
            else:
                print ("Timestamp column is missing from second dataframe")

        else:
            print("Timestamp column is missing from first dataframe")


    def extractFeatures(self,timestamp,log_df,speech_df,ip_list):

        user1 = ip_list[0]
        user2 = ip_list[1]
        user3 = ip_list[2]
        user4 = ip_list[3]

        # features
        user1_addition = 0
        user1_deletion = 0
        user1_text = ""

        user2_addition = 0
        user2_deletion = 0
        user2_text = ""

        user3_addition = 0
        user3_deletion = 0
        user3_text = ""

        user4_addition = 0
        user4_deletion = 0
        user4_text = ""


        user1_speaking_time = 0
        user2_speaking_time = 0
        user3_speaking_time = 0
        user4_speaking_time = 0

        speaking_sequence=""

        u1 = log_df.loc[log_df['ip']==user1,:]
        u2 = log_df.loc[log_df['ip']==user2,:]
        u3 = log_df.loc[log_df['ip']==user3,:]
        u4 = log_df.loc[log_df['ip']==user4,:]



        us1 = speech_df.loc[speech_df['users']==1,:]
        us2 = speech_df.loc[speech_df['users']==2,:]
        us3 = speech_df.loc[speech_df['users']==3,:]
        us4 = speech_df.loc[speech_df['users']==4,:]


        def concatenate_list_data(list):

            result= ''
            for element in list:
                if str(element) != 'nan':
                    result += str(element)
            return result




        user1_addition = u1.addition.sum()
        user1_deletion = u1.deletion.sum()
        user1_text = concatenate_list_data(u1.charbank.tolist())

        user2_addition = u2.addition.sum()
        user2_deletion = u2.deletion.sum()
        user2_text = concatenate_list_data(u2.charbank.tolist())

        user3_addition = u3.addition.sum()
        user3_deletion = u3.deletion.sum()
        user3_text = concatenate_list_data(u3.charbank.tolist())

        user4_addition = u4.addition.sum()
        user4_deletion = u4.deletion.sum()
        user4_text = concatenate_list_data(u4.charbank.tolist())

        user1_speaking = us1.users.sum()*float(200/1000)
        user2_speaking = us2.users.sum()*float(200/1000)
        user3_speaking = us3.users.sum()*float(200/1000)
        user4_speaking = us4.users.sum()*float(200/1000)

        speaking_sequence = speech_df['users'].tolist()


        return {'timestamp':timestamp,'u1_add':user1_addition,'u1_del':user1_deletion,'u1_text':user1_text,'u2_add':user2_addition,'u2_del':user1_deletion,'u2_text':user2_text,'u3_add':user3_addition,'u3_del':user1_deletion,'u3_text':user3_text,'u4_add':user4_addition,'u4_del':user1_deletion,'u4_text':user4_text,'u1_speak':user1_speaking,'u2_speak':user2_speaking,'u3_speak':user3_speaking,'u4_speak':user4_speaking,'speak_sequence':speaking_sequence}



    def displayCrossSpaceBehavior(self,merged_file="Final.csv", ip_list=[],window="30S"):

        df = self.mergeLogSpeech(ip_list=['192.168.1.235','192.168.1.193','',''],window_size=window,write_file=False)
        #print(df)
        df = df.set_index(pd.DatetimeIndex(df['timestamp']))
        df[['u1_add','u2_add','u3_add','u4_add']].plot(kind='bar')
        df[['u1_del','u2_del','u3_del','u4_del']].plot(kind='bar')
        df[['u1_speak','u2_speak','u3_speak','u4_speak']].plot(kind='bar')
        plt.show()


    def displayNetworkOverTime(self,window):
        df = self.mergeLogSpeech(ip_list=['192.168.1.235','192.168.1.193','',''],window_size=window,write_file=False)
        fig = plt.figure(figsize=(15,5))

        for i in range(df.shape[0]):
            #print(df['speak_sequence'][i])
            ax = fig.add_subplot(1,df.shape[0],(i+1))
            edges = self.generateEdgeFile(seq=df['speak_sequence'][i])
            a = self.drawNetwork({1:df['u1_speak'][i],2:df['u2_speak'][i],3:df['u3_speak'][i],4:df['u4_speak'][i]},edges)
            ax.title.set_text(df['timestamp'][i])
        plt.show()




lg = Log_Speech_Analyzer(log_file='log_data.csv',speech_file = 'test_data.CSV')

lg.displayNetworkOverTime('60S')
