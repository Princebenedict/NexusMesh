import { readFileSync } from "fs";
import path from "path";
import {
  TransactionHash,
  TransactionStatus,
  GenLayerClient,
  DecodedDeployData,
} from "genlayer-js/types";

const safeJson = (value: unknown) =>
  JSON.stringify(
    value,
    (_, v) => (typeof v === "bigint" ? v.toString() : v),
    2
  );

export default async function main(client: GenLayerClient<any>) {
  console.log("Deploying NexusMesh to GenLayer Bradbury...");

  const filePath = path.resolve(process.cwd(), "contracts/NexusMesh.py");
  const contractCode = new Uint8Array(readFileSync(filePath));

  const deployTransaction = await client.deployContract({
    code: contractCode,
    args: [250],
  });

  console.log("Transaction sent:", deployTransaction);
  console.log("Waiting for confirmation...");

  const receipt = await client.waitForTransactionReceipt({
    hash: deployTransaction as TransactionHash,
    retries: 200,
  });

  const statusName =
    (receipt as any).statusName ?? (receipt as any).status_name;
  const txExecutionResultName =
    (receipt as any).txExecutionResultName ??
    (receipt as any).tx_execution_result_name;

  const contractAddress =
    (receipt.txDataDecoded as DecodedDeployData | undefined)?.contractAddress ??
    (receipt as any).data?.contract_address;

  if (
    statusName !== TransactionStatus.ACCEPTED &&
    statusName !== TransactionStatus.FINALIZED
  ) {
    throw new Error(
      `Deployment failed. Status: ${statusName}. Receipt: ${safeJson(receipt)}`
    );
  }

  if (!contractAddress) {
    throw new Error(
      `Deployment accepted but no contract address was found. Receipt: ${safeJson(receipt)}`
    );
  }

  console.log("");
  console.log("NexusMesh deployment completed");
  console.log("Contract Address:", contractAddress);
  console.log("Transaction Hash:", deployTransaction);

  if (txExecutionResultName && txExecutionResultName !== "SUCCESS") {
    console.log("Execution Result:", txExecutionResultName);
  }

  return contractAddress;
}
