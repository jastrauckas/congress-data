
for i in $(seq 100 111); do 
  DIR='data/'
  DIR+=$i
  mkdir -p $DIR

  CMD='rsync -avz --delete --delete-excluded --exclude **/text-versions/ govtrack.us::govtrackdata/congress/'
  CMD+=$i
  CMD+='/votes data/'
  CMD+=$i
  $CMD

  CMD2=$(echo $CMD | sed "s/votes/bills/g")
  $CMD2

  find . -name "*.xml" -type f|xargs rm -f 

done
