# EQ12 Advanced Development Container with VB Debugging
FROM mcr.microsoft.com/dotnet/sdk:8.0

# Environment for VB debugging and development
ENV EQ12_VB_DEBUG=true
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12
RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
       # Python and development
       python3.12 python3.12-pip python3.12-venv python3-pip \
       # VB.NET and Mono for VB debugging
       mono-complete mono-vbnc mono-mcs mono-debugger nuget \
       # Standard development tools
       git curl wget unzip nodejs npm \
       # Browser automation dependencies
       libnss3 libatk-bridge2.0-0 libxkbcommon0 libdrm2 \
       libxcomposite1 libxrandr2 libgbm1 libasound2 xvfb \
       # Additional development utilities
       jq tree htop vim nano zip build-essential \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python3.12
RUN ln -sf /usr/bin/python3.12 /usr/bin/python3

# Install Python packages for EQ12 development
RUN python3 -m pip install --upgrade pip && python3 -m pip install \
    playwright==1.47.0 \
    fastapi uvicorn \
    pytest black flake8 mypy pylint coverage pytest-cov \
    requests beautifulsoup4 selenium argparse pathlib

# Install Playwright browsers
RUN python3 -m playwright install chromium

# Install Node.js development tools
RUN npm install -g chrome-devtools-protocol typescript eslint prettier nodemon

# Install .NET project templates for VB development
RUN dotnet new --install Microsoft.DotNet.Web.ProjectTemplates

# Create VB debugging workspace structure
WORKDIR /workspace
RUN mkdir -p logs scripts tests configs vb_projects dotnet_tools data dashboard

# Create VB debugging template with hardcoded best practices
RUN echo 'Option Strict On\nOption Explicit On\n\n'"'"'EQ12 VB Debugging Template - Hardcoded Best Practices\nImports System\n\nPublic Class EQ12VBDebugTemplate\n    Public Shared Sub Main()\n        Debug.WriteLine("Container Template Starting")\n        Try\n            Dim result As String = ProcessContainerData("test")\n            Debug.WriteLine("Result: " & result)\n        Catch ex As Exception\n            Debug.WriteLine("Exception: " & ex.Message)\n        End Try\n    End Sub\n    \n    Private Shared Function ProcessContainerData(input As String) As String\n        If String.IsNullOrEmpty(input) Then\n            Return "ERROR_EMPTY"\n        End If\n        Return "PROCESSED_" & input.ToUpper()\n    End Function\nEnd Class' > vb_projects/EQ12_VB_Debug_Template.vb

# Set working directory
WORKDIR /workspace