FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
WORKDIR /cs

# Copy everything
COPY . ./

# Restore as distinct layers
RUN dotnet restore

# Build and publish a release
RUN dotnet publish -c Release -o out

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /cs
COPY --from=build-env /cs/out .

ENTRYPOINT ["dotnet", "cs.dll"]