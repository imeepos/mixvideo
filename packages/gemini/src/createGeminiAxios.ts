import axios from "axios";
import { createDefaultGoogleGenaiClient } from "./google-genai-client";

export function useGeminiAxios() {
    return axios.create({
        baseURL: `https://bowongai-dev--bowong-ai-video-gemini-fastapi-webapp.modal.run`,
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

export async function uploadFileToGemini(bucket: string, prefix: string, file: Buffer) {
    const genminiAxios = useGeminiAxios()
    await genminiAxios.request({
        method: `post`,
        url: `/google/vertex-ai/upload`,
        params: {
            bucket: bucket,
            prefix: prefix
        },
        data: {
            file: file
        },
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

export async function useGemini() {
    const token = await useGeminiAccessToken()
    return createDefaultGoogleGenaiClient(token.access_token)
}
