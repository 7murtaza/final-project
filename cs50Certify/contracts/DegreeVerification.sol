// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract DegreeVerification {
    struct Degree {
        bool exists;
        address owner;
        string rollNo;
        string name;
    }

    mapping(bytes32 => Degree) private degrees;
    mapping(string => mapping(string => bytes32)) private rollNoToHash; 
    uint public fee = 0.00001 ether; 

    // Event when a degree is uploaded
    event DegreeUploaded(bytes32 degreeHash, address indexed owner, string rollNo, string name);
    
    // Event when a degree is revoked
    event DegreeRevoked(bytes32 degreeHash, address indexed owner);

    // Modifier to ensure the user pays the correct fee
    modifier requiresFee() {
        require(msg.value >= fee, "Insufficient fee paid.");
        _;
    }

    // Function to upload or update degree (requires fee)
    function uploadDegree(bytes32 degreeHash, string memory rollNo, string memory name) external payable requiresFee {
    bytes32 existingHash = rollNoToHash[rollNo][name];
    if (degrees[existingHash].exists) {
        require(existingHash == degreeHash, "This degree is already uploaded with different data.");
    }

    degrees[degreeHash] = Degree({
        exists: true,
        owner: msg.sender,
        rollNo: rollNo,
        name: name
    });

    rollNoToHash[rollNo][name] = degreeHash;

    emit DegreeUploaded(degreeHash, msg.sender, rollNo, name);
}


    // Function to verify a degree (requires fee)
    function verifyDegree(bytes32 degreeHash) external payable requiresFee returns (bool) {
        return degrees[degreeHash].exists;
    }

    // Function to check if a degree exists
    function isDegreeExists(bytes32 degreeHash) external view returns (bool) {
        return degrees[degreeHash].exists;
    }

    // Function to retrieve the degree hash by roll number and name
    function getDegreeHashByRollNumberAndName(string memory rollNo, string memory name) external view returns (bytes32) {
        return rollNoToHash[rollNo][name];
    }

    // Function to revoke a degree by roll number and name
    function revokeDegree(bytes32 degreeHashData) external {
        bytes32 degreeHash = degreeHashData;
        require(degrees[degreeHash].owner == msg.sender, "Only the owner can revoke the degree.");
        require(degrees[degreeHash].exists, "Degree does not exist.");

        // Delete the degree and roll number-to-hash mapping
        delete degrees[degreeHash];

        emit DegreeRevoked(degreeHash, msg.sender);
    }
    
}
