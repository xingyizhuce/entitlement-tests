#!/bin/sh

usage() {
    echo "Usage: $0 cdn|CDN|eus|EUS|sat6|SAT6|sat5|SAT5|rhn|RHN"
    exit 1
}

get_ip() {
    ip_file="$WORKSPACE/RESOURCES.txt"
    if [ -f "$ip_file" ]; then
        System_IP=`cat $ip_file | grep EXISTING_NODES  | awk -F '=' '{print $2}'`
        if [ "$System_IP" != "" ]; then
            export System_IP=$System_IP
            echo "Succeed to get beaker IP: $System_IP."
        else
            echo "ERROR: Failed to get the IP of beaker system!"
            exit 1
        fi
    else
        echo "ERROR: $ip_file does not exist, Failed to get the ip of beaker system!"
        exit 1
    fi
}

prepare_cdn() {
    # Trying to get beaker testing system ip and export it into env variant 'System_IP'
    get_ip

    if [ "$PID" == "" ]; then
        # Get PID from manifest for current arch and varaint
        python $WORKSPACE/entitlement-tests/analyze_testing.py pid
        PID=`cat PID.txt`
    fi

    # Print params
    echo "PID=$PID"
    echo "Variant=$Variant"
    echo "Arch=$Arch"
    echo "Manifest_URL=$Manifest_URL"
    echo "Distro=$Distro"
    echo "CDN=$CDN"
    echo "Candlepin=$Candlepin"
    echo "Test_Type=$Test_Type"
    echo "Release_Version=$Release_Version"

    cdn_test_case_path=$WORKSPACE/entitlement-tests/CDN/Tests/
    cdn_test_suite=$WORKSPACE/entitlement-tests/test_cdn.py
    cdn_case_template=$WORKSPACE/entitlement-tests/CDN/case_template/CDNEntitlement_template.py

    # Generate all test cases from template for cdn testing, and add test cases to test suite
    OLD_IFS="$IFS"
    IFS=","
    PID_array=($PID)
    IFS="$OLD_IFS"
    for pid in ${PID_array[@]}
    do
        echo "Ready to generate test case for PID $pid"
        case_name=CDNEntitlement_${pid}
        case_full_name=${cdn_test_case_path}${case_name}.py

        # Generate test case
        cp $cdn_case_template $case_full_name
        sed -i -e "s/PID/$pid/g" -e "s/VARIANT/$Variant/g" -e "s/ARCH/$Arch/g" $case_full_name

        # Add import sentence to __init__.py
        if [ "`cat $cdn_test_suite | grep $case_name`" ==  "" ]; then sed -i "2a\from CDN.Tests.$case_name import $case_name" $cdn_test_suite; fi

        # Add test cases to test suite
        line="suite.addTest(CDNEntitlement_${pid}('testCDNEntitlement_${Variant}_${Arch}_${pid}'))"
        if [ "`cat $cdn_test_suite | grep $case_name | grep -v import`" == "" ]; then sed -i "/suite = unittest.TestSuite()/a\    $line" $cdn_test_suite; fi
    done
}

prepare_openshift() {
    # Trying to get beaker testing system ip and export it into env variant 'System_IP'
    get_ip

    if [ "$PID" == "" ]; then
        # Get PID from manifest for current arch and varaint
        python $WORKSPACE/entitlement-tests/analyze_testing.py pid
        PID=`cat PID.txt`
    fi

    # Print params
    echo "PID=$PID"
    echo "Variant=$Variant"
    echo "Arch=$Arch"
    echo "Manifest_URL=$Manifest_URL"
    echo "Distro=$Distro"
    echo "CDN=$CDN"
    echo "Candlepin=$Candlepin"
    echo "Test_Type=$Test_Type"
    echo "Release_Version=$Release_Version"

    cdn_test_case_path=$WORKSPACE/entitlement-tests/CDN/Tests/
    cdn_test_suite=$WORKSPACE/entitlement-tests/test_cdn.py
    cdn_case_template=$WORKSPACE/entitlement-tests/CDN/case_template/CDNEntitlement_openshift_template.py

    # Generate all test cases from template for cdn testing, and add test cases to test suite
    OLD_IFS="$IFS"
    IFS=","
    PID_array=($PID)
    IFS="$OLD_IFS"
    for pid in ${PID_array[@]}
    do
        echo "Ready to generate test case for PID $pid"
        case_name=CDNEntitlement_${pid}
        case_full_name=${cdn_test_case_path}${case_name}.py

        # Generate test case
        cp $cdn_case_template $case_full_name
        sed -i -e "s/PID/$pid/g" -e "s/VARIANT/$Variant/g" -e "s/ARCH/$Arch/g" $case_full_name

        # Add import sentence to __init__.py
        if [ "`cat $cdn_test_suite | grep $case_name`" ==  "" ]; then sed -i "2a\from CDN.Tests.$case_name import $case_name" $cdn_test_suite; fi

        # Add test cases to test suite
        line="suite.addTest(CDNEntitlement_${pid}('testCDNEntitlement_${Variant}_${Arch}_${pid}'))"
        if [ "`cat $cdn_test_suite | grep $case_name | grep -v import`" == "" ]; then sed -i "/suite = unittest.TestSuite()/a\    $line" $cdn_test_suite; fi
    done
}

prepare_eus() {
    # Trying to get beaker testing system ip and export it into env variant 'System_IP'
    get_ip

    if [ "$PID" == "" ]; then
        # Get PID from manifest for current arch and varaint
        python $WORKSPACE/entitlement-tests/analyze_testing.py pid
        PID=`cat PID.txt`
    fi

    # Print params
    echo "PID=$PID"
    echo "Variant=$Variant"
    echo "Arch=$Arch"
    echo "Manifest_URL=$Manifest_URL"
    echo "Distro=$Distro"
    echo "CDN=$CDN"
    echo "Candlepin=$Candlepin"
    echo "Test_Type=$Test_Type"
    echo "Release_Version=$Release_Version"

    eus_test_case_path=$WORKSPACE/entitlement-tests/CDN/EUS_Tests/
    eus_test_suite=$WORKSPACE/entitlement-tests/test_eus.py
    eus_case_template=$WORKSPACE/entitlement-tests/CDN/case_template/EUSEntitlement_template.py

    # Generate all test cases from template for eus testing, and add test cases to test suite
    OLD_IFS="$IFS"
    IFS=","
    PID_array=($PID)
    IFS="$OLD_IFS"
    for pid in ${PID_array[@]}
    do
        echo "Ready to generate eus test case for PID $pid"
        case_name=EUSEntitlement_${pid}
        case_full_name=${eus_test_case_path}${case_name}.py

        # Generate test case
        cp $eus_case_template $case_full_name
        sed -i -e "s/PID/$pid/g" -e "s/VARIANT/$Variant/g" -e "s/ARCH/$Arch/g" $case_full_name

        # Add import sentence to __init__.py
        if [ "`cat $eus_test_suite | grep $case_name`" == "" ]; then sed -i "2a\from CDN.EUS_Tests.$case_name import $case_name" $eus_test_suite; fi

        # Add test cases to test suite
        line="suite.addTest(EUSEntitlement_${pid}('testEUSEntitlement_${Variant}_${Arch}_${pid}'))"; echo $line;echo $Variant; echo $Arch
        if [ "`cat $eus_test_suite | grep $case_name | grep -v import`" == "" ]; then sed -i "/suite = unittest.TestSuite()/a\    $line" $eus_test_suite; fi

        echo "End to add eus test case for PID $pid"
    done
}

prepare_sat6() {
    # Trying to get beaker testing system ip and export it into env variant 'System_IP'
    get_ip

    if [ "$PID" == "" ]; then
        # Get PID from manifest for current arch and varaint
        python $WORKSPACE/entitlement-tests/analyze_testing.py pid
        PID=`cat PID.txt`
    fi

    # Print params
    echo "PID=$PID"
    echo "Variant=$Variant"
    echo "Arch=$Arch"
    echo "Manifest_URL=$Manifest_URL"
    echo "Distro=$Distro"
    echo "SAT6_Server_Hostname=$SAT6_Server_Hostname"
    echo "SAT6_Server_IP=$SAT6_Server_IP"
    echo "SAT6_Server_Username=$SAT6_Server_Username"
    echo "SAT6_Server_Password=$SAT6_Server_Password"
    echo "SAT6_Server_OrgLabel=$SAT6_Server_OrgLabel"
    echo "Test_Type=$Test_Type"
    echo "Release_Version=$Release_Version"

    sat6_test_case_path=$WORKSPACE/entitlement-tests/SAT6/Tests/
    sat6_test_suite=$WORKSPACE/entitlement-tests/test_sat6.py
    sat6_case_template=$WORKSPACE/entitlement-tests/SAT6/case_template/SAT6Entitlement_template.py

    # Generate all test cases from template for sat6 testing, and add test cases to test suite
    OLD_IFS="$IFS"
    IFS=","
    PID_array=($PID)
    IFS="$OLD_IFS"
    for pid in ${PID_array[@]}
    do
        echo "Ready to generate test case for PID $pid"
        case_name=SAT6Entitlement_${pid}
        case_full_name=${sat6_test_case_path}${case_name}.py

        # Generate test case
        cp $sat6_case_template $case_full_name
        sed -i -e "s/PID/$pid/g" -e "s/VARIANT/$Variant/g" -e "s/ARCH/$Arch/g" $case_full_name

        # Add import sentence to __init__.py
        if [ "`cat $sat6_test_suite | grep $case_name`" ==  "" ]; then sed -i "2a\from SAT6.Tests.$case_name import $case_name" $sat6_test_suite; fi

        # Add test cases to test suite
        line="suite.addTest(SAT6Entitlement_${pid}('testSAT6Entitlement_${Variant}_${Arch}_${pid}'))"
        if [ "`cat $sat6_test_suite | grep $case_name | grep -v import`" == "" ]; then sed -i "/suite = unittest.TestSuite()/a\    $line" $sat6_test_suite; fi
    done
}

prepare_sat5() {
    echo "Prepare testing: export testing system ip into env variant 'System_IP' and replace variant in test case script."
    # Trying to get beaker testing system ip and export it into env variant 'System_IP'
    get_ip
    echo "Testing system IP or hostname:"
    echo "System_IP=$System_IP"

    # Print params
    echo "Testing parameters:"
    echo "Variant=$Variant"
    echo "Arch=$Arch"
    echo "Manifest_URL=$Manifest_URL"
    echo "Distro=$Distro"
    echo "SAT5_Server=$SAT5_Server"
    echo "SAT5_Server_Username=$SAT5_Server_Username"
    echo "SAT5_Server_Password=$SAT5_Server_Password"
    echo "SAT5_Activation_Key=$SAT5_Activation_Key"
    echo "Product_Type=$Product_Type"
    echo "Test_Level=$Test_Level"
    echo "Test_Type=$Test_Type"

    sat5_test_case=$WORKSPACE/entitlement-tests/SAT5/Tests/SAT5Entitlement.py
    sat5_test_suite=$WORKSPACE/entitlement-tests/test_sat5.py

    # Replace VARIANT and ARCH in rhn test suite and test case
    sed -i -e "s/VARIANT/$Variant/g" -e "s/ARCH/$Arch/g" $sat5_test_case $sat5_test_suite
}

prepare_rhn() {
    # Trying to get beaker ip
    get_ip

    # Print params
    echo "Variant=$Variant"
    echo "Arch=$Arch"
    echo "Manifest_URL=$Manifest_URL"
    echo "Distro=$Distro"
    echo "RHN=$RHN"

    rhn_test_case=$WORKSPACE/entitlement-tests/RHN/Tests/RHNEntitlement.py
    rhn_test_suite=$WORKSPACE/entitlement-tests/test_rhn.py

    # Replace VARIANT and ARCH in rhn test suite and test case
    sed -i -e "s/VARIANT/$Variant/g" -e "s/ARCH/$Arch/g" $rhn_test_case $rhn_test_suite
}

if [ $# -eq 1 ] ; then
    param=$1
    case $param in
        cdn | CDN)
            echo "call function prepare_cdn"
            prepare_cdn;;
        eus | EUS)
            echo "call function prepare_eus"
            prepare_eus;;
        sat6 | SAT6)
            echo "call function prepare_sat6"
            prepare_sat6;;
        sat5 | SAT5)
            echo "call function prepare_sat5"
            prepare_sat5;;
        rhn | RHN)
            echo "call function prepare_rhn"
            prepare_rhn;;
        openshift | OPENSHIFT)
            echo "call function prepare_openshift"
            prepare_openshift;;
        container)
            echo "call function get_ip"
            get_ip;;
        *)
            usage;;
    esac
else
    usage
fi
