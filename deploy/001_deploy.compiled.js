import { readFileSync } from "fs";
import path from "path";
import {
  TransactionStatus
} from "genlayer-js/types";
import { testnetBradbury } from "genlayer-js/chains";
const safeJson = (value) => JSON.stringify(
  value,
  (_, v) => typeof v === "bigint" ? v.toString() : v,
  2
);
async function main(client) {
  console.log("\u{1F680} Deploying NexusMesh to GenLayer Bradbury...");
  const filePath = path.resolve(process.cwd(), "contracts/NexusMesh.py");
  const contractCode = new Uint8Array(readFileSync(filePath));
  await client.initializeConsensusSmartContract();
  const deployTransaction = await client.deployContract({
    code: contractCode,
    args: [250]
  });
  console.log("\u{1F4E1} Transaction sent:", deployTransaction);
  console.log("\u23F3 Waiting for confirmation (this may take 30-90s)...");
  const receipt = await client.waitForTransactionReceipt({
    hash: deployTransaction,
    retries: 200
  });
  if (receipt.statusName !== TransactionStatus.ACCEPTED && receipt.statusName !== TransactionStatus.FINALIZED) {
    throw new Error(
      `Deployment failed. Status: ${receipt.statusName}. Receipt: ${safeJson(receipt)}`
    );
  }
  const contractAddress = client.chain.id !== testnetBradbury.id ? receipt.data?.contract_address : receipt.txDataDecoded?.contractAddress;
  if (!contractAddress) {
    throw new Error(
      `Could not determine deployed contract address. Receipt: ${safeJson(receipt)}`
    );
  }
  console.log("");
  console.log("\u2705 NexusMesh deployed successfully on Bradbury!");
  console.log("\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501");
  console.log("Contract Address:", contractAddress);
  console.log("Transaction Hash:", deployTransaction);
  console.log("\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501");
  console.log("\u{1F4CB} Copy the Contract Address into frontend/index.html");
  return contractAddress;
}
export {
  main as default
};
