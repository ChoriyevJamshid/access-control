import axios from "axios";

export const login = async (username: string, password: string) => {
  const { data } = await axios.post("http://localhost:8000/api/token/", { username, password });
  return data;
};