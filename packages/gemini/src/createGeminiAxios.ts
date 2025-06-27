import axios from "axios";
import { createDefaultGoogleGenaiClient } from "./google-genai-client";
const MODAL_URL = `https://bowongai-dev--bowong-ai-video-gemini-fastapi-webapp.modal.run` as const;
export function useGeminiAxios() {
    return axios.create({
        baseURL: MODAL_URL,
        headers: {
            Authorization: `Bearer bowong7777`,
        }
    })
}

export async function useGeminiAccessToken(): Promise<{ access_token: string, expires_in: number, token_type: string }> {
    const geminiAxios = useGeminiAxios()
    const token = await geminiAxios.request({
        method: `get`,
        url: `/google/access-token`
    }).then(res => res.data)
    return token;
}
import FormData from 'form-data'
export interface GeminiUploadResult {
    kind: string,
    id: string,
    selfLink: string,
    mediaLink: string,
    name: string,
    bucket: string,
    generation: string,
    metageneration: string,
    contentType: string,
    storageClass: string,
    size: 11825150,
    md5Hash: string,
    crc32c: string,
    etag: string,
    timeCreated: string,
    updated: string,
    timeStorageClassUpdated: string,
    timeFinalized: string,
    urn: string
}
export async function uploadFileToGemini(bucket: string, prefix: string, formData: FormData): Promise<GeminiUploadResult> {
    const token = await useGeminiAccessToken()
    const genminiAxios = axios.create({
        baseURL: MODAL_URL,
        headers: {
            ...formData.getHeaders(),
            Authorization: `Bearer ${token.access_token}`,
            [`x-google-api-key`]: token.access_token,
        }
    })
    const result = await genminiAxios.request({
        method: `post`,
        url: `/google/vertex-ai/upload`,
        params: {
            bucket: bucket,
            prefix: prefix
        },
        data: formData,
    })
    return result.data
}

export async function useGemini() {
    const token = await useGeminiAccessToken()
    return createDefaultGoogleGenaiClient(token.access_token)
}
