import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import urllib, base64
from django.shortcuts import render, redirect
from .forms import CSVFileForm
from .models import CSVFile

def home(request):
    return redirect('upload_file')

def upload_file(request):
    if request.method == 'POST':
        form = CSVFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('analyze_data')
    else:
        form = CSVFileForm()
    return render(request, 'analysis/upload.html', {'form': form})

def analyze_data(request):
    csv_file = CSVFile.objects.latest('uploaded_at')
    df = pd.read_csv(csv_file.file.path)

    # Perform basic data analysis
    head = df.head().to_html()
    summary = df.describe().to_html()
    missing_values = df.isnull().sum().to_frame('missing_values').to_html()

    # Generate histogram for numerical columns
    fig, ax = plt.subplots()
    sns.histplot(df.select_dtypes(include=['float64', 'int64']), kde=True, ax=ax)
    plt.tight_layout()

    # Save plot to a PNG image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    context = {
        'head': head,
        'summary': summary,
        'missing_values': missing_values,
        'plot': uri,
    }
    return render(request, 'analysis/results.html', context)
