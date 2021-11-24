FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build
WORKDIR /app

COPY src/*.sln .
COPY src/Service/*.csproj ./Service/
COPY src/DataLayer/*.csproj ./DataLayer/
RUN dotnet restore

COPY src/. .
WORKDIR /app/Service
RUN dotnet publish -c Release -o publish
COPY src/Service/Views/. ./publish/Views

FROM mcr.microsoft.com/dotnet/aspnet:5.0 AS runtime
WORKDIR /app

COPY --from=build /app/Service/publish ./
RUN mkdir logs && chmod 777 -R ./logs

RUN adduser --system --home /app --shell /usr/sbin/nologin --no-create-home --disabled-password -u 10000 ctfland
USER ctfland


ENTRYPOINT ["dotnet", "Service.dll"]
