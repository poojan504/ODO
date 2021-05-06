from oscpy.server import OSCThreadServer
from time import sleep
from sklearn.cluster import DBSCAN
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import math
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib as mpl
from pythonosc import udp_client
def send_to_max(tag,message,ip,port):
    #print("############",tag)
    try:
        client = udp_client.SimpleUDPClient("2.1.0.2", 8000)
        #print("############nnn")
        client.send_message(tag, message)
    except Exception as e:
        pass
        #print(e)
    finally:
        return True
def send_to_chat(tag,message,ip,port):
    #print("############",tag)
    try:
        client = udp_client.SimpleUDPClient("2.1.0.10", 7403)
        #print("############nnn")
        client.send_message(tag, message)
    except Exception as e:
        #print(e)
        pass
    finally:
        return True

def clustering(Y):
    global max_ip
    global max_port
    Y = list(Y)
    X = []
    #print(Y)
    for i in range(0,len(Y),2):
        X.append([Y[i],Y[i+1]])
    db = DBSCAN(eps=0.3, min_samples=2).fit(X)
    #print(db.labels_)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    #print('Estimated number of clusters:', n_clusters_)
    #print('Estimated number of isolated people: %d',n_noise_)
    #send_to_max("/cluster",'Estimated number of clusters: ' + str(n_clusters_),max_ip,max_port)
    #send_to_max("/cluster",'Estimated number of isolated people: ' +str(n_noise_),max_ip,max_port)
    send_to_max("/cluster",str(n_noise_) + " "  + str(n_clusters_),max_ip,max_port)
    try:
        pass
        #print("Silhouette Coefficient: %0.3f"
        #% metrics.silhouette_score(X, labels))
    except:
        pass
        #print("People are well separated")
    # Black removed and is used for noise instead.
    #unique_labels = set(labels)
    #colors = [plt.cm.Spectral(each)
    #      for each in np.linspace(0, 1, len(unique_labels))]
    #for k, col in zip(unique_labels, colors):
    #    if k == -1:
        # Black used for noise.
    #        col = [0, 0, 0, 1]

    #class_member_mask = (labels == k)

    #xy = X[class_member_mask & core_samples_mask]
    #plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
    #         markeredgecolor='k', markersize=14)

    #xy = X[class_member_mask & ~core_samples_mask]
    #plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
    #         markeredgecolor='k', markersize=6)

    #plt.title('Estimated number of clusters: %d' % n_clusters_)
    #plt.show()
def cluster_desity(Y):
    #if sum(Y) == 0:
    #    return
    #Cluster Density
    # I have a question here. Is the average distance computer for all the individual or only indvidual within a clus
    global max_ip
    global max_port
    Y = list(Y)
    X = []
    for i in range(0,len(Y),2):
        X.append([Y[i],Y[i+1]])
    average_distance = []
    for i in X:
        minn = 100
        for j in X:
            distance = float("{0:.2f}".format(math.sqrt(((i[0]-j[0])**2)+((i[1]-j[1])**2) )))
            if distance < minn  and distance != 0:
                minn = distance
        average_distance.append(minn)
    #print("The average of minimum distance is: ", sum(average_distance)/5)
    #send_to_max("/density","The average of minimum distance is: " +str(sum(average_distance)/5),max_ip,max_port)
    send_to_max("/density","The average of minimum distance is: " +str(sum(average_distance)/5),max_ip,max_port)
def mobility_and_speed(X_,Y_):
    #if sum(Y_) == 0 and sum(X_):
    #    return
    X = []
    Y = []
    for i in range(0,len(Y_),2):
        Y.append([Y_[i],Y_[i+1]])
    for i in range(0,len(X_),2):
        X.append([X_[i],X_[i+1]])
    positions_new_np = np.asarray(X)
    positions_old_np = np.asarray(Y)
    speed = []
    for i in range(0,len(Y)):
        distance = float("{0:.4f}".format(math.sqrt(((Y[i][0]-X[i][0])**2)+((Y[i][1]-X[i][1])**2) )))
        speed.append((distance/(5)))
    #speed = (positions_new_np - positions_old_np)/5
    #print(positions_new_np,"new_np")
    #print(positions_old_np)
    #print(speed)
    positions_new_str = np.array2string(positions_new_np)
    positions_old_str = np.array2string(positions_old_np)
    speed_str = np.array2string(np.asarray(speed))
    out = ""
    #print(len(positions_new_str))
    #print(len(positions_old_str))
    for i,k in zip(range(len(positions_new_str)),range(len(speed))):
        out = out + " " + str(positions_new_np[i][0]) + " " + str(positions_new_np[i][1]) + " " + str(positions_old_np[i][0]) + " " + str(positions_old_np[i][1]) + " " + str(speed[k]*100)
    #if out.count('0') < 500:
    send_to_max("/velocity",out,max_ip,max_port)
    acceleration_from_position(speed,1)

def acceleration_from_position(new_vel,t_i):
    out = ""
    global old_vel
    global max_ip
    global max_port
    for i in range(len(new_vel)):
       # out += str(int((new_vel[i] - old_vel[i])*100/1)) + " "i
       out += str(float("{0:.2f}".format((new_vel[i] - old_vel[i])*100/1))) + " "
    #acc = (new_vel - old_vel)/t_i
    old_vel = new_vel
    #if out.count('0') < 10:
    send_to_max("/crowd_accel", out,max_ip,max_port)
def positional_data(values):
    global positions_df
    values = values.decode()
    values = values.split(' ')
    #print(values)
    pd_new = pd.Series(values, index = positions_df.columns)
    positions_df = positions_df.append(pd_new, ignore_index=True)

def acceleration_data(values):
    global accelerations_df
    values = values.decode()
    values = values.split(' ')
    pd_new = pd.Series(values, index = accelerations_df.columns)
    accelerations_df = accelerations_df.append(pd_new, ignore_index=True)
    positions = []
    for i in range(0,len(values),1):
        positions.append([values[i]])
    #print("got accelaration values: {}".format(values))

def average_acceleration(values):
    pass

def receive_values_from_max(ip,port):
  while(1):
    osc = OSCThreadServer()
    sock = osc.listen(address = ip,port = port, default = True)
    #osc.bind(b'/crowd-accel',acceleration_data)
    osc.bind(b'/crowd-pos',positional_data)
    sleep(1)
    osc.stop()
    return True

if __name__ == "__main__":
    max_ip = "192.168.0.48"
    max_port = 8001
    send_to_max("/crowd", "ready",max_ip,max_port)    
    positions_mean_old  = pd.DataFrame([[0,0,0,0,0,0,0,0,0,0]])
    accelerations_df = pd.DataFrame([[0,0,0,0,0]])
    positions_mean_old = np.mean(positions_mean_old.values.astype(float),axis=0)
    max_ip = "192.168.0.48"
    max_port = 8001
    old_vel = [0,0,0,0,0]
    while(1):
        positions_df = pd.DataFrame([[0,0,0,0,0,0,0,0,0,0]])
        accelaration_df = pd.DataFrame([0,0,0,0,0])
        batch = receive_values_from_max('2.1.0.13',7400)
        positions_mean_present = np.mean(positions_df.values.astype(float),axis=0)
        clustering(positions_mean_present)
        cluster_desity(positions_mean_present)
        mobility_and_speed(positions_mean_present,positions_mean_old)
        if batch:
            positions_mean_old = positions_mean_present
        #sleep(1)
