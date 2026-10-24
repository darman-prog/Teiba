"""Endpoint del agente Sage."""
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request

from app.agent.loop import AgentRunner
from app.api.deps import get_agent_runner
from app.schemas import ConsultaRequest, ConsultaResponse

router = APIRouter(tags=["agente"])


@router.post("/agente/consulta", response_model=ConsultaResponse)
def consultar(
    body: ConsultaRequest,
    request: Request,
    runner: Annotated[AgentRunner, Depends(get_agent_runner)],
) -> ConsultaResponse:
    trace_id = getattr(request.state, "trace_id", "") or uuid4().hex
    resultado = runner.consultar(body.pregunta, trace_id)
    return ConsultaResponse(**resultado)
