traffics="stag1_0.2_0.3 stag2_0.2_0.3 stag1_0.4_0.3 stag2_0.4_0.3 stag1_0.5_0.3 stag2_0.5_0.3 random1_1 random1_2 random2_1 random2_2"

from="./genetico_results/result_8"
to="./results/result_8"
target="Genetico_100_10_0.6_0.25"

for traffic in $traffics
do
  target_path="${to}/$traffic/Genetico"

  if [ ! -d $out_dir ]
  then
    sudo mkdir $target_path
  fi

  sudo cp -vrf "${from}/$traffic/${target}/." "$target_path"
done
