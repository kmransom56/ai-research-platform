# 1. Nuclear fix for NodeSource duplicates
sudo rm -f /etc/apt/sources.list.d/nodesource.*
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/nodesource.gpg
echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.sources

# 2. Fix Yarn GPG completely
sudo rm -f /etc/apt/sources.list.d/yarn.list
sudo apt-key del 72ECF46A56B4AD39C907BBB71646B01B86E50310 2>/dev/null || true
curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/yarn.gpg
echo "deb [signed-by=/usr/share/keyrings/yarn.gpg] https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

# 3. Nuclear fix for .NET conflicts
sudo apt remove --purge dotnet* aspnetcore* netstandard* -y
sudo apt autoremove -y
sudo apt clean

# 4. Update and test
sudo apt update
