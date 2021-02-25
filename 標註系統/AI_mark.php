<?php
/// Page Created by CGU Amor_Kai 2016 12 15
header('Content-Type: application/json; charset=UTF-8');
function dbconnect()
{
    $MONGODB_DB_HOST = "fpgindexer2.widelab.org";
    $MONGODB_DB_NAME = "webpage_dataset";
    $MONGODB_PORT = 27021;
    $MONGODB_USER = "webpageDatasetMaster";
    $MONGODB_PASSWORD = "webpageDatasetMasterPassword";

    // 連線到 MongoDB 伺服器
    return new MongoDB\Driver\Manager('mongodb://'.$MONGODB_USER.':'.$MONGODB_PASSWORD.'@'.$MONGODB_DB_HOST.':'.$MONGODB_PORT.'/'.$MONGODB_DB_NAME);
    
}

if($_POST["action"] == "select"){
    Select();
}
else if($_POST["action"] == "update"){
    Update();
}

function Select(){
    $Collection=$_POST['Collection'];
    $Language=$_POST['Language'];
    //$Collection="News";
    $db = dbconnect();
    #$filter= array('language' => "ZH_CHT");
    $filter= array('language' => array('$regex' => $Language), 'manual_labeling' => array('$not' => array('$size' => 2)));
    
    $options = array(
    'limit' => 100,
    'sort'  => array ('keyword_density' => -1)
    );
    $query = new MongoDB\Driver\Query($filter, $options);
    $result = $db->executeQuery('webpage_dataset.'.$Collection, $query);
    $index=1;
    $all=array();
    $out=array();
    $result_num=0;
    foreach($result as $k => $row) {
        $data["ID"] = $row->hash_value;
        $data["Link"] = $row->link;
        $data["Title"] = $row->title;
        $data["keyword_density"] = $row->keyword_density;
        $data["contents"] = $row->contents;
        array_push($all,$data);
        unset($data);
        $result_num++;
    }
    if($result_num>10){
        $numbers=array();
        while(count($numbers)<10){
            $numbers[]=mt_rand(1,$result_num);
            $numbers=array_unique($numbers);
            sort($numbers);
        }
        for( $i=0 ; $i<10 ; $i++ ) {
            array_push($out,$all[$numbers[$i]-1]);
            $filename=$i+1;
            $contents="<meta charset='utf-8'>";
            $myfile = fopen("HTML/".$filename.".html", "w") or die("Unable to open file!");
            fwrite($myfile, $contents.$all[$numbers[$i]-1]["contents"]);
            fclose($myfile);
        }
    }
    else{
        $out=$all;
    }
    #print_r($numbers);
    #print_r($out);
    echo json_encode(array('isSuccess' => true, "out"=>$out)); 
}

function Update(){
    $ID=$_POST['label_ID'];
    $label_index=$_POST['label_value'];
    $Collection=$_POST['Collection'];
    $db = dbconnect();
    for($i=0 ; $i<count($ID) ; $i++){
        if($label_index[$i]=='1'){
            $label="others";
        }
        else if($label_index[$i]=='2'){
            $label="ai";
        }
        else if($label_index[$i]=='3'){
            $label="internet of things";
        }
        else if($label_index[$i]=='4'){
            $label="advanced materials";
        }
        else if($label_index[$i]=='5'){
            $label="quantum computer";
        }
        else if($label_index[$i]=='6'){
            $label="formosa plastics";
        }
        $bulk = new MongoDB\Driver\BulkWrite;
        $bulk->update(
            ['hash_value' => $ID[$i]],
            ['$push' => ['manual_labeling' => $label]]
        );
        $result = $db->executeBulkWrite('webpage_dataset.'.$Collection, $bulk);
    }
    echo json_encode(array('isSuccess' => true)); 
}





?>