#!/bin/bash

# Define colors
c1="\e[92m"  # Green
c2="\e[32m"  # Dark Green
c3="\e[33m"  # Yellow
reset="\e[0m"

# ASCII Art for Bodhi Linux Logo (Improved)
ascii_art="${c1}|           ${c2},,mmFORAMBENmm,, 
${c1}'      ${c2},aKKP${c1}LL*|L${c2}TKp,
  ${c1}t  ${c2}aKP${c1}L**\\\`          \\\`**L${c2}*Kp
   IX${c1}EL${c3}L,wwww,              ${c1}\\*||${c2}Kp
 ,#P${c1}L|${c3}KKKpPP@IPPTKmw,          ${c1}\`*||${c2}K
,K${c1}LL*${c3}{KKKKKKPPb\$KPhpKKPKp        ${c1}\`||${c2}K
#${c1}PL  ${c3}!KKKKKKPhKPPP\$KKEhKKKKp      ${c1}\`||${c2}K
!H${c1}L*   ${c3}1KKKKKKKphKbPKKKKKK\$KKp      ${c1}\`|I${c2}W
\$${c1}bL     ${c3}KKKKKKKKBQKhKbKKKKKKKK       ${c1}|I${c2}N
\$${c1}bL     ${c3}!KKKKKKKKKKNKKKKKKKPP\`       ${c1}|I${c2}b
TH${c1}L*     ${c3}TKKKKKK##KKKN@KKKK^         ${c1}|I${c2}M
K@${c1}L      ${c3}*KKKKKKKKKKKEKE5          ${c1}||${c2}K
\`NL${c1}L      ${c3}\KKKKKKKKKK\'''|L       ${c1}||${c2}#P
 \K@${c1}LL       ${c3}\\"\"\`        ${c1}'.   :||${c2}#P
   Yp${c1}LL                      ${c1}' |L${c2}\$M\`
    \`Tp${c1}pLL,                ,|||${c2}p'L
       \"Kpp${c1}LL++,.,    ,,|||\$${c2}#K*   ${c1}'
          ${c2}\\"MKPansuriya#KM\"\        ${c1}\h,\\\${reset}"

# Get system info
OS=$(lsb_release -ds)
HOSTNAME=$(hostname)
KERNEL=$(uname -r)
UPTIME=$(uptime -p)
PACKAGES=$(dpkg --get-selections | wc -l)
SHELL=$(echo $SHELL)
RESOLUTION=$(xdpyinfo | grep dimensions | awk '{print $2}')
WM="Moksha"
DE="Enlightenment"
WM_THEME="MokshaPassion"
THEME="Flat-Remix-GTK-Green-Dark [GTK2/3]"
ICONS="Papirus-Dark [GTK2/3]"
TERMINAL="terminology"
FONT="Noto Mono"
CPU=$(awk -F ': ' '/model name/ {print $2; exit}' /proc/cpuinfo)
GPU=$(lspci | grep -i 'VGA' | cut -d ':' -f3)
MEMORY=$(free -m | awk '/Mem:/ {printf "%dMiB / %dMiB\n", $3, $2}')

# Print output with proper formatting
echo " "
paste <(echo -e "$ascii_art") <(
echo -e "\e[92mOS:\e[0m $OS
\e[92mHost:\e[0m $HOSTNAME
\e[92mKernel:\e[0m $KERNEL
\e[92mUptime:\e[0m $UPTIME
\e[92mPackages:\e[0m $PACKAGES (apt)
\e[92mShell:\e[0m $SHELL
\e[92mResolution:\e[0m $RESOLUTION
\e[92mDE:\e[0m $DE
\e[92mWM:\e[0m $WM
\e[92mWM Theme:\e[0m $WM_THEME
\e[92mTheme:\e[0m $THEME
\e[92mIcons:\e[0m $ICONS
\e[92mTerminal:\e[0m $TERMINAL
\e[92mTerminal Font:\e[0m $FONT
\e[92mCPU:\e[0m $CPU
\e[92mGPU:\e[0m $GPU
\e[92mMemory:\e[0m $MEMORY"
) | expand -t 40

echo " "
echo " "