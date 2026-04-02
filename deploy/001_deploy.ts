import { readFileSync } from "fs";
import path from "path";
import { GenLayerClient } from "genlayer-js/types";

const FIXED_FRONTEND_CONTRACT = "0x9026f734759602B4D4Fec05497e259B852ebf540";

export default async function main(client: GenLayerClient<any>) {
  console.log("Deploying NexusMesh to GenLayer Bradbury...");
  console.log("Frontend is pinned to fixed contract address:", FIXED_FRONTEND_CONTRACT);
  console.log("If you deploy a new contract, the frontend will still keep using the fixed address above until you intentionally change the code.");

  const filePath = path.resolve(process.cwd(), "contracts/NexusMesh.py");
  const contractCode = new Uint8Array(readFileSync(filePath));

  const deployTransaction = await client.deployContract({
    code: contractCode,
    args: [250],
  });

  console.log("");
  console.log("Deploy transaction sent successfully.");
  console.log("Transaction Hash:", deployTransaction);
  console.log("");
  console.log("Receipt lookup is being skipped because waitForTransactionReceipt()");
  console.log("is failing on getTransactionAllData in your current SDK/network setup.");
  console.log("");
  console.log("Next step:");
  console.log("1. Check the tx hash in Bradbury explorer");
  console.log("2. Confirm whether the deployment succeeded");
  console.log("3. Frontend remains permanently pinned to:", FIXED_FRONTEND_CONTRACT);
  console.log("4. Only change the frontend contract address later if you intentionally want to move away from the fixed contract");

  return deployTransaction;
}





