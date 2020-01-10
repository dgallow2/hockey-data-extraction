# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 14:27:25 2020

@author: Jared Van Blitterswyk
"""

import numpy as np
import pandas as pd
import requests
import json
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt

results = []
for game_id in range(2019020613, 2019020614, 1): # this is currently set up to process on game (current game to current game +1)
    url = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game_id)
    r = requests.get(url)
    game_data = r.json()
    
    # --------- allocate memory to arrays where results stored ----------------
    player_id = {} # keeps a directory of all skater names and their inforomation
    results = [] # only 
    shotOnTarget = [] # keeps track of total number of shots on target in the game
    shotOnTargetHome = [] # stores total number of shots on target in the game for home team
    shotOnTargetAway = [] # stores track of total number of shots on target in the game for away team
    shotCoords = [] # stores coordinates of all shots taken in the game
    shotCoordsHome = [] # stores coordinates of all shots taken by home team (including goals)
    shotCoordsAway = [] # stores coordinates of all shots taken by away team (including goals)
    shotCoordsGoalHome = [] # stores coordinates of all goals by home team
    shotCoordsGoalAway = [] # stores coordinates of all goals by away team
    shooter = {} # stores list of names of shooters for all shot events (n/a for non-shots)
    shooterID = {} # list of names of shooters associated with shot events
    shooterOnTargetHome = [] # list of names of shooters associated with home shot on target
    shooterGoalHome = [] # list of names of goal scorers from home team
    shooterGoalAway = [] # list of names of goal scorers from away team
    shooterOnTargetAway = [] # list of names of shooters associated with away shot on target
    shooterMissHome = [] # list of names of shooters associated with home missed shot
    shooterMissAway = [] # list of names of shooters associated with home missed shot
    shot_id = 0
    

    for x in ['home','away']:
        player_dict = game_data.get('liveData').get('boxscore').get('teams').get(x).get('skaters')
        player_id[x] = player_dict
        
    for y in player_id:
        for playerID in player_id[y]:
            play_dict = game_data.get('liveData').get('boxscore').get('teams').get(y).get('players').get('ID' + str(playerID)).get('person')
            results.append(play_dict)
    
    # extract names of home and away teams - used later to sort shots and goals events    
    hometeam = game_data.get('liveData').get('boxscore').get('teams').get('home').get('team').get('name')
    awayteam = game_data.get('liveData').get('boxscore').get('teams').get('away').get('team').get('name')       
            
    # list of all events in a game        
    for rows in game_data:
        allPlays = game_data.get('liveData').get('plays').get('allPlays')
    
    # allocate memory for shotCoords based on number of total plays 
        # data structure: 
        # index 0 = shot (target = 1, miss = 0, non-shot event = 2 - used for filtering events)
        # index 1 = x coordinate of shot
        # index 2 = y coordinate of shot
                       
    shotCoords = np.zeros((len(allPlays), 3)) 
    shotCoordsHome = np.zeros((len(allPlays), 3))
    shotCoordsGoalHome = np.zeros((len(allPlays), 3))
    shotCoordsGoalAway = np.zeros((len(allPlays), 3))
    shotCoordsAway = np.zeros((len(allPlays), 3))
    
    for a in range(0,len(allPlays)): # loop through all events in `allPlays' array
        if allPlays[a].get('result').get('event') == 'Shot' or allPlays[a].get('result').get('event') == 'Goal': # if the event is a shot
            player_id = allPlays[a].get('players')[0].get('player').get('fullName') # player who took shot
            shooter[a] = player_id # store in array containing name of all shooters
            shotOnTarget.append(1) # add one to the array tracking all shots on target
            period = allPlays[a].get('about').get('period')
            
            # store data according to structure listed above
            shotCoords[a,0]=1
            shotCoords[a,1]=float(allPlays[a].get('coordinates').get('x'))
            shotCoords[a,2]=float(allPlays[a].get('coordinates').get('y'))
            
            if allPlays[a].get('team').get('name') == hometeam and allPlays[a].get('result').get('event') == 'Goal':
                if period <= 4:
                    # store data according to structure listed above
                    shotCoordsGoalHome[a,0]=1
                    if period == 1 or period ==3:
                        shotCoordsGoalHome[a,1]=float(allPlays[a].get('coordinates').get('x'))*-1
                        shotCoordsGoalHome[a,2]=float(allPlays[a].get('coordinates').get('y'))
                    else:
                        shotCoordsGoalHome[a,1]=float(allPlays[a].get('coordinates').get('x'))
                        shotCoordsGoalHome[a,2]=float(allPlays[a].get('coordinates').get('y'))
                    shooterGoalHome.append(allPlays[a].get('players')[0].get('player').get('fullName'))
            elif allPlays[a].get('team').get('name') == awayteam and allPlays[a].get('result').get('event') == 'Goal':
                if period <= 4:
                    # store data according to structure listed above
                    shotCoordsGoalAway[a,0]=1
                    if period == 1 or period == 3:
                        shotCoordsGoalAway[a,1]=float(allPlays[a].get('coordinates').get('x'))*-1
                        shotCoordsGoalAway[a,2]=float(allPlays[a].get('coordinates').get('y')) 
                    else:
                        shotCoordsGoalAway[a,1]=float(allPlays[a].get('coordinates').get('x'))
                        shotCoordsGoalAway[a,2]=float(allPlays[a].get('coordinates').get('y')) 
                    shooterGoalAway.append(allPlays[a].get('players')[0].get('player').get('fullName'))
            # sort shots into arrays for respective teams according to data structure listed above
            # period 1 and 3 for the home team are listed as shooting to the left - bring all home team shots to the left side of the rink
            # ---------- home team ----------
            if allPlays[a].get('team').get('name') == hometeam and (period == 1 or period == 3):
                shotCoordsHome[a,0]=1
                shotCoordsHome[a,1]=float(allPlays[a].get('coordinates').get('x'))*-1
                shotCoordsHome[a,2]=float(allPlays[a].get('coordinates').get('y'))
                shooterOnTargetHome.append(player_id)
                                
            elif allPlays[a].get('team').get('name') == hometeam and (period == 2 or period == 4):
                shotCoordsHome[a,0]=1
                shotCoordsHome[a,1]=float(allPlays[a].get('coordinates').get('x'))
                shotCoordsHome[a,2]=float(allPlays[a].get('coordinates').get('y'))
                shooterOnTargetHome.append(player_id)
                
            # ---------- away team ----------
            # period 1 and 3 for the away team are listed as shooting to the right - bring all away team shots to the right side of the rink
            elif allPlays[a].get('team').get('name') == awayteam and (period == 1 or period == 3):
                shotCoordsAway[a,0]=1
                shotCoordsAway[a,1]=float(allPlays[a].get('coordinates').get('x'))*-1
                shotCoordsAway[a,2]=float(allPlays[a].get('coordinates').get('y'))
                shooterOnTargetAway.append(player_id)
                                
            elif allPlays[a].get('team').get('name') == awayteam and (period == 2 or period == 4):
                shotCoordsAway[a,0]=1
                shotCoordsAway[a,1]=float(allPlays[a].get('coordinates').get('x'))
                shotCoordsAway[a,2]=float(allPlays[a].get('coordinates').get('y'))
                shooterOnTargetAway.append(player_id)       

        elif allPlays[a].get('result').get('event') == 'Missed Shot': # if the event is a missed shot
            player_id = allPlays[a].get('players')[0].get('player').get('fullName') # player who took shot
            shooter[a] = player_id # store in array containing name of all shooters
            shotOnTarget.append(0) # add zero to the array tracking all shots on target
            
            # store data according to structure listed above
            shotCoords[a,0]=0
            shotCoords[a,1]=float(allPlays[a].get('coordinates').get('x'))
            shotCoords[a,2]=float(allPlays[a].get('coordinates').get('y'))
            
            shotCoordsGoalHome[a,0]=0
            shotCoordsGoalHome[a,1]=0
            shotCoordsGoalHome[a,2]=0
            
            shotCoordsGoalAway[a,0]=0
            shotCoordsGoalAway[a,1]=0
            shotCoordsGoalAway[a,2]=0
            
            # sort shots into arrays for respective teams according to data structure listed above
            # period 1 and 3 for the home team are listed as shooting to the left - bring all home team shots to the left side of the rink
            # ---------- home team ---------
            if allPlays[a].get('team').get('name') == hometeam and (period == 1 or period == 3):
                shotCoordsHome[a,0]=0
                shotCoordsHome[a,1]=float(allPlays[a].get('coordinates').get('x'))*-1
                shotCoordsHome[a,2]=float(allPlays[a].get('coordinates').get('y'))
                
            elif allPlays[a].get('team').get('name') == hometeam and (period == 2 or period == 4):
                shotCoordsHome[a,0]=0
                shotCoordsHome[a,1]=float(allPlays[a].get('coordinates').get('x'))
                shotCoordsHome[a,2]=float(allPlays[a].get('coordinates').get('y'))
                
            # ---------- away team ----------
            # period 1 and 3 for the away team are listed as shooting to the right - bring all away team shots to the right side of the rink
            elif allPlays[a].get('team').get('name') == awayteam and (period == 1 or period == 3):
                shotCoordsAway[a,0]=0
                shotCoordsAway[a,1]=float(allPlays[a].get('coordinates').get('x'))*-1
                shotCoordsAway[a,2]=float(allPlays[a].get('coordinates').get('y'))
                
            elif allPlays[a].get('team').get('name') == awayteam and (period == 2 or period == 4):
                shotCoordsAway[a,0]=0
                shotCoordsAway[a,1]=float(allPlays[a].get('coordinates').get('x'))
                shotCoordsAway[a,2]=float(allPlays[a].get('coordinates').get('y'))  
            
        else: # if the event is a non shot/goal event
            shotCoords[a,0:] = [2, 0, 0] # assign first value to 2 to indicate no shot attempt
            shotCoordsGoalHome[a,0:] = [2, 0, 0] # assign first value to 2 to indicate no shot attempt
            shotCoordsGoalAway[a,0:] = [2, 0, 0] # assign first value to 2 to indicate no shot attempt
            shooter[a] = 'N/A'

    # ----- data sorting and truncating procedures for plotting/export --------
    shotCoords = shotCoords[shotCoords[:, 0] != 2] # remove rows in array that include 2 in first column (no shot attempt)
    shotCoordsGoalHome = shotCoordsGoalHome[shotCoordsGoalHome[:, 0] != 2] # remove rows in array that include 2 in first column (no shot attempt)
    shotCoordsGoalAway = shotCoordsGoalAway[shotCoordsGoalAway[:, 0] != 2] # remove rows in array that include 2 in first column (no shot attempt)
    
    # find only shooter names associated with shots on target and missed shots
    for i in range(0,len(shooter)):
        if shooter[i] != 'N/A':
            shooterID[i] = shooter[i]
            
    shotsOnTargetCoords = shotCoords[shotCoords[:,0] == 1] # keep shots on target coordinates where shot on target occured (1 in first column)
    shotsOnTargetCoords = shotsOnTargetCoords[:,1:] # truncate shots on target coordinates to only x and y values
    missedShotsCoords = shotCoords[shotCoords[:,0] == 0] # keep shots on target coordinates where missed shot occured (0 in first column)
    missedShotsCoords = missedShotsCoords[:,1:] # truncate missed shot coordinates to only x and y values
    
    # ---------- home team ----------
    # shots on target
    shotsOnTargetCoordsHome = shotCoordsHome[shotCoordsHome[:,0] == 1] # keep shots on target coordinates where shot on target occured (1 in first column)
    shotsOnTargetCoordsHome = shotsOnTargetCoordsHome[:,1:] # truncate shots on target coordinates to only x and y values
    # missed shots
    missedShotsCoordsHome = shotCoordsHome[shotCoordsHome[:,0] == 0] # keep shots on target coordinates where missed shot occured (0 in first column)
    missedShotsCoordsHome = missedShotsCoordsHome[:,1:] # truncate missed shot coordinates to only x and y values
    # goals
    goalCoordsHome = shotCoordsGoalHome[shotCoordsGoalHome[:,0] == 1] # keep goal coordinates (1 in first column)
    goalCoordsHome = goalCoordsHome[:,1:] # truncate goal coordinates to only x and y values
    
    
    # ---------- away team ----------
    # shots on target
    shotsOnTargetCoordsAway = shotCoordsAway[shotCoordsAway[:,0] == 1] # keep shots on target coordinates where shot on target occured (1 in first column)
    shotsOnTargetCoordsAway = shotsOnTargetCoordsAway[:,1:] # truncate shots on target coordinates to only x and y values
    # missed shots
    missedShotsCoordsAway = shotCoordsAway[shotCoordsAway[:,0] == 0] # keep shots on target coordinates where missed shot occured (0 in first column)
    missedShotsCoordsAway = missedShotsCoordsAway[:,1:] # truncate missed shot coordinates to only x and y values
    # goals
    goalCoordsAway = shotCoordsGoalAway[shotCoordsGoalAway[:,0] == 1] # keep goal coordinates where shot on target occured (1 in first column)
    goalCoordsAway = goalCoordsAway[:,1:] # truncate goal coordinates to only x and y values
    
    
    # -------------------------------------------------------------------------
    # ------------------------ plot shot chart --------------------------------
    # plot shots on target and missed shots on same figure (all shots and goals)
    #fig = plt.figure(figsize=[4, 1.5],facecolor='white') # figure size in inches
    #ax = fig.add_axes([0, 0, 1, 1])
    #plt.scatter(shotsOnTargetCoords[:,0],shotsOnTargetCoords[:,1],c = (0.1,0.1,0.7))
    #plt.scatter(missedShotsCoords[:,0],missedShotsCoords[:,1],c = (0.7,0.1,0.1))
    #ax.set_ylim([-42.5, 42.5])
    #ax.set_xlim([-100, 100])
    
    # plot shots overlaid on rink image (home shots displayed on left, away shots on right)
    img = plt.imread("hockey_rink_diagram.jpg")
    fig, ax = plt.subplots()
    ax.imshow(img[:img.shape[0]-15, 4:img.shape[1]-4],extent=[0, 400, 0, 170])
    plt.scatter((shotsOnTargetCoordsHome[:,0]+100)*2,(shotsOnTargetCoordsHome[:,1]+42.5)*2,c = (0.7,0.9,0.7), edgecolors = (0.1,0.4,0.1), label='Home: Shot on Target')
    plt.scatter((missedShotsCoordsHome[:,0]+100)*2,(missedShotsCoordsHome[:,1]+42.5)*2,c = (0.9,0.7,0.7), edgecolors = (0.4,0.1,0.1), label='Home: Missed Shot')
    plt.scatter((goalCoordsHome[:,0]+100)*2,(goalCoordsHome[:,1]+42.5)*2, c = (0.1,0.4,0.1), marker = 'o', edgecolors = (0.1,0.4,0.1), label='Home: Goal')
    plt.scatter((shotsOnTargetCoordsAway[:,0]+100)*2,(shotsOnTargetCoordsAway[:,1]+42.5)*2,c = (0.7,0.9,0.7), marker = '<', edgecolors = (0.1,0.4,0.1), label='Away: Shot on Target')
    plt.scatter((missedShotsCoordsAway[:,0]+100)*2,(missedShotsCoordsAway[:,1]+42.5)*2,c = (0.9,0.7,0.7), marker = '<', edgecolors = (0.4,0.1,0.1), label='Away: Missed Shot')
    plt.scatter((goalCoordsAway[:,0]+100)*2,(goalCoordsAway[:,1]+42.5)*2,c = (0.1,0.4,0.1), marker = '<', edgecolors = (0.1,0.4,0.1), label='Away: Goal')
    plt.axis('off')
    plt.text(20, -15, 'Home: '+hometeam, fontsize = 10)
    plt.text(240, -15, 'Away:' +awayteam, fontsize = 10)
    plt.legend(ncol = 2,loc='lower center', bbox_to_anchor=(0.47, -0.5))
    plt.savefig('ShotChart_BOSvsNJD_12312019.png', dpi=800)