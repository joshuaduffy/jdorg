import axios, { AxiosPromise } from 'axios';

export const httpClient = axios.create({
  baseURL: 'http://localhost:5000',
});

export interface IGetTitleResponse {
  title: string;
}

export const getTitleApi = ():AxiosPromise<IGetTitleResponse> => {
  return httpClient.get('/title');
};
