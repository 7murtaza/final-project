const DegreeVerification = artifacts.require("./DegreeVerification.sol");

module.exports = function (deployer) {
  deployer.deploy(DegreeVerification).then((instance) => {
    console.log("Contract deployed at address:", instance.address);
  });
};
