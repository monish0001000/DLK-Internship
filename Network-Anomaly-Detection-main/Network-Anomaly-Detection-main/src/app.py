import tkinter as tk
from tkinter import messagebox
import subprocess
import pandas as pd

def preprocess():
    subprocess.run(["python3", "preprocess.py"])
    messagebox.showinfo("Success", "Data Preprocessed Successfully!")

def train():
    subprocess.run(["python3", "train.py"])
    messagebox.showinfo("Success", "Model Trained Successfully!")

def visualize():
    subprocess.run(["python3", "visualize.py"])

def show_result():
    data = pd.read_csv("/home/kali/Network-Anomaly-Detection/dataset/anomaly_results.csv")

    normal = (data["Anomaly"] == "Normal").sum()
    anomaly = (data["Anomaly"] == "Anomaly").sum()

    result.config(text=f"Normal Packets : {normal}\nAnomaly Packets : {anomaly}")

root = tk.Tk()
root.title("Network Traffic Anomaly Detection")
root.geometry("500x420")

title = tk.Label(
    root,
    text="Network Traffic Anomaly Detection",
    font=("Arial", 18, "bold")
)
title.pack(pady=15)

tk.Button(root, text="1. Preprocess Data",
          command=preprocess,
          width=30).pack(pady=8)

tk.Button(root, text="2. Train Model",
          command=train,
          width=30).pack(pady=8)

tk.Button(root, text="3. Show Graph",
          command=visualize,
          width=30).pack(pady=8)

tk.Button(root, text="4. Show Results",
          command=show_result,
          width=30).pack(pady=8)

result = tk.Label(root,
                  text="",
                  font=("Arial", 12))
result.pack(pady=20)

root.mainloop()
