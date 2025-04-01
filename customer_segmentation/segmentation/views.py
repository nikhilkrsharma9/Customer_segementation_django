import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UploadFileForm
from .models import CustomerData
from django.contrib import messages

def handle_uploaded_file(f):
    path = os.path.join(settings.MEDIA_ROOT, f.name)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path

def create_plots(df, n_clusters):
    # Standardize features
    features = ['Annual Income (k$)', 'Spending Score (1-100)']
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply K-Means
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Create plots
    plots = {}
    
    # Elbow Method Plot
    plt.figure(figsize=(10, 6))
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
        kmeans.fit(X_scaled)
        wcss.append(kmeans.inertia_)
    plt.plot(range(1, 11), wcss, marker='o', linestyle='--')
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    elbow_plot = get_graph()
    plots['elbow'] = elbow_plot
    plt.close()
    
    # 2D Cluster Plot
    plt.figure(figsize=(10, 6))
    for i in range(n_clusters):
        plt.scatter(df[df['Cluster'] == i]['Annual Income (k$)'], 
                   df[df['Cluster'] == i]['Spending Score (1-100)'], 
                   label=f'Cluster {i}')
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], 
               s=300, c='yellow', label='Centroids')
    plt.title('Customer Segments (2D)')
    plt.xlabel('Annual Income (k$)')
    plt.ylabel('Spending Score (1-100)')
    plt.legend()
    cluster_plot = get_graph()
    plots['cluster'] = cluster_plot
    plt.close()
    
    # Cluster Distribution Plot
    plt.figure(figsize=(8, 5))
    sns.countplot(x='Cluster', data=df, palette='viridis')
    plt.title('Customer Distribution Across Clusters')
    plt.xlabel('Cluster')
    plt.ylabel('Number of Customers')
    distribution_plot = get_graph()
    plots['distribution'] = distribution_plot
    plt.close()
    
    return plots, df.head(10).to_html(classes='table table-striped')

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            try:
                df = pd.read_csv(instance.file.path)
                required_columns = ['Annual Income (k$)', 'Spending Score (1-100)']
                if not all(col in df.columns for col in required_columns):
                    messages.error(request, "CSV file must contain 'Annual Income (k$)' and 'Spending Score (1-100)' columns")
                    instance.delete()
                    return redirect('upload')
                
                return render(request, 'segmentation/elbow.html', {
                    'file_id': instance.id,
                    'elbow_plot': create_elbow_plot(df)
                })
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                instance.delete()
                return redirect('upload')
    else:
        form = UploadFileForm()
    return render(request, 'segmentation/upload.html', {'form': form})

def process_clusters(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        n_clusters = int(request.POST.get('n_clusters'))
        
        try:
            instance = CustomerData.objects.get(id=file_id)
            df = pd.read_csv(instance.file.path)
            plots, table_html = create_plots(df, n_clusters)
            
            instance.cluster_count = n_clusters
            instance.save()
            
            return render(request, 'segmentation/results.html', {
                'plots': plots,
                'table_html': table_html,
                'n_clusters': n_clusters
            })
        except Exception as e:
            messages.error(request, f"Error processing clusters: {str(e)}")
            return redirect('upload')
    return redirect('upload')

def create_elbow_plot(df):
    features = ['Annual Income (k$)', 'Spending Score (1-100)']
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
        kmeans.fit(X_scaled)
        wcss.append(kmeans.inertia_)
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 11), wcss, marker='o', linestyle='--')
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plot = get_graph()
    plt.close()
    return plot