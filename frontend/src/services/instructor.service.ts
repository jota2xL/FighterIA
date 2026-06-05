import apiClient from "./api.client";
import type {
  InstructorGroup,
  GroupCreate,
  GroupStudent,
  StudentDetail,
  CommentCreate,
  InstructorComment,
} from "@/types/instructor.types";

export const instructorService = {
  getGroups: () =>
    apiClient.get<InstructorGroup[]>("/instructor/groups").then((r) => r.data),

  createGroup: (data: GroupCreate) =>
    apiClient
      .post<InstructorGroup>("/instructor/groups", data)
      .then((r) => r.data),

  getGroupStudents: (groupId: number) =>
    apiClient
      .get<GroupStudent[]>(`/instructor/groups/${groupId}/students`)
      .then((r) => r.data),

  getStudentDetail: (studentId: number) =>
    apiClient
      .get<StudentDetail>(`/instructor/students/${studentId}`)
      .then((r) => r.data),

  addComment: (data: CommentCreate) =>
    apiClient
      .post<InstructorComment>("/instructor/comments", data)
      .then((r) => r.data),

  joinGroup: (inviteCode: string) =>
    apiClient
      .post("/instructor/groups/join", { invite_code: inviteCode })
      .then((r) => r.data),

  removeStudent: (groupId: number, studentId: number) =>
    apiClient
      .delete(`/instructor/groups/${groupId}/students/${studentId}`)
      .then((r) => r.data),
};
