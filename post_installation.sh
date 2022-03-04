#!/bin/sh
finish() {
    echo "[i] Endtime:      $(date)"
    echo "\nThanks for playing the dns_ctf!"
    exit 0
}
restart() {
    echo "[i] Endtime:      $(date)"
    for pid in $(ps -ax | grep main.py | grep -v grep | awk '{ print $1 }'); do kill $pid; done
    echo -n "[i] Restarting Container "
    for i in `seq 1 10`
    do
        echo -n "."
        sleep 0.5
    done
    # Run Admin interface
    (python3 /opt/DarknetStore/Admin/main.py 1> /dev/null 2> /dev/null &)
    # Run Customer interface
    su -c '(authbind --deep /usr/bin/python3 /opt/DarknetStore/Interface/main.py 1> /dev/null 2> /dev/null &)' flask
    echo "\n[i] Starttime:    $(date)"
    echo -n "[noob@dns_ctf /]$ "
}
info() {
    echo "\n==Usage=="
    echo "  - \e[1;39minfo\e[0m: Prints this page"
    echo "  - \e[1;39mrestart\e[0m: Restarts both flask servers"
    echo "  - \e[1;39mflags\e[0m: Get challenge information"
    echo "  - \e[1;39mquit\e[0m: Exit the Container"
    echo ""
    echo "==Info=="
    echo "  - No bruteforce needed (except for 1 time)"
    echo "  - SSH access is not mandatory, but helpful"
    echo "  - In case of bugs, rerun (not build) the container"
    echo "  - In case of questions: \e[1;31m!¡!\e[0mI H4T3 QU3ST10N5\e[1;31m!¡!\e[0m"
    echo ""
}
flags() {
    echo "\n==Flags=="
    echo "  #1 PiMails - 100P - bet you can't see the forest for the trees?"
    echo "  #2 Flask - 200P - let's play hide and seek"
    echo "  #3 Schatten - 200P - watch your shadow!"
    echo "  #4 groß ins tief - 250P - don't log back"
    echo "  #5 Priv Esc - 300P - back to the roots"
    echo "  #6 IDOR - 300P - from the base to the top"
    echo "  #7 Schlüsseldienst - 500P - Don't loose 'em, or you have to ring the key service"
    echo ""
}

# Start SSH Daemon on configured port 443
/usr/local/sbin/sshd
# Set Access Control Level for User flask on /etc/shadow,
# allowing access to this file via XXE and RCE.
setfacl -m u:flask:r /etc/shadow
chown -R pi:pi /opt/Keyring/

chown root:root /root/flag.txt
chmod 700 /root/flag.txt

mkhomedir_helper flask
echo -n "ITS{gg_f0r_fl45k1ng_4r0und}" > /home/flask/.flag.txt
chown flask:flask /home/flask/.flag.txt
chmod 700 /home/flask/.flag.txt

# Run Admin interface
(python3 /opt/DarknetStore/Admin/main.py 1> /dev/null 2> /dev/null &)
# Run Customer interface
su -c '(authbind --deep /usr/bin/python3 /opt/DarknetStore/Interface/main.py 1> /dev/null 2> /dev/null &)' flask

echo " ______   _        _______    _______ _________ _______ "
echo "(  __  \ ( (    /|(  ____ \  (  ____ \\__   __/(  ____  \\"
echo "| (  \  )|  \  ( || (    \/  | (    \/   ) (   | (    \/"
echo "| |   ) ||   \ | || (_____   | |         | |   | (__    "
echo "| |   | || (\ \) |(_____  )  | |         | |   |  __)   "
echo "| |   ) || | \   |      ) |  | |         | |   | (      "
echo "| (__/  )| )  \  |/\____) \__/ (____/\   | |   | )      "
echo "(______/ |/    )_)\__________________/   )_(   |/       "
echo "                                                        "
echo "                               (c) 2022 - TA,MS,JM,JS   "
echo "[i] Enter \e[1;31mquit\e[0m to kill the Container"
echo "[i] Enter \e[1;31mrestart\e[0m to restart the Container"
echo "[i] Enter \e[1;31minfo\e[0m to get some help"
echo "[i] Enter \e[1;31mflags\e[0m to get an overview on the challenges"
echo "[i] This shell is \e[1;39mNOT\e[0m part of the CTF"
echo ""
echo "[i] Container IP: \e[1;31m$(cat /etc/hosts | grep $(hostname) | awk '{ print $1 }')\e[0m"
echo "[i] Starttime:    $(date)"
echo -n "[noob@dns_ctf /]$ "
while read answer
do
    case $answer in
        restart)
            restart
        ;;
        quit)
            finish
        ;;
        info)
            info
            echo -n "[noob@dns_ctf /]$ "
        ;;
        flags)
            flags
            echo -n "[noob@dns_ctf /]$ "
        ;;
        *)
            echo "[!] Only commands [\e[1;31mrestart\e[0m|\e[1;31mquit\e[0m|\e[1;31minfo\e[0m|\e[1;31mflags\e[0m] are available\n    This is \e[1;39mNOT\e[0m part of the CTF"
            echo -n "[noob@dns_ctf /]$ "
        ;;
    esac
done
