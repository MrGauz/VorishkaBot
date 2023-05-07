# TGS converter from a C# project
FROM mcr.microsoft.com/dotnet/sdk:7.0 AS tgs_converter_build

WORKDIR /source
COPY ./tgs_converter .

RUN dotnet publish -c Release -r linux-x64 --self-contained true -o /converter

# Telegram bot running in python
FROM python:3.10-slim-buster
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    # Install .NET 7.0 runtime
    && apt-get install -y curl libunwind8 gettext \
    && curl -SL https://dotnetcli.azureedge.net/dotnet/Runtime/7.0.3/dotnet-runtime-7.0.3-linux-x64.tar.gz --output dotnet.tar.gz \
    && mkdir -p /opt/dotnet && tar zxf dotnet.tar.gz -C /opt/dotnet \
    && ln -s /opt/dotnet/dotnet /usr/local/bin \
    && rm -rf dotnet.tar.gz \
    # Install other dependencies
    && apt-get install --no-install-recommends -y \
      ffmpeg \
      tzdata \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

COPY --from=tgs_converter_build /converter /converter
RUN chmod +x /converter/TgsConverter.dll

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]
