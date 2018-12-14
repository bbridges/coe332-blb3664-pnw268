Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_check_update = false
  config.vm.hostname = "coe332-project.box"
  config.vm.network "public_network"

  config.vm.provision :docker
end
