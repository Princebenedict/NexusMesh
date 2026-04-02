import { readFileSync } from "fs";
import path from "path";
import { GenLayerClient } from "genlayer-js/types";

export default async function main(client: GenLayerClient<any>) {
  console.log("Deploying NexusMesh to GenLayer Bradbury...");

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
  console.log("2. If deployment succeeded, copy the contract address from explorer");
  console.log("3. Paste that address into the frontend Config modal");

  return deployTransaction;
}




