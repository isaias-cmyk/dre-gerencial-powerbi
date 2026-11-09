let
    Datas = List.RemoveNulls(fLancamentos[competencia_data] & fOrcamento[competencia_data] & fPrevisao[competencia_data]),
    Inicio = if List.IsEmpty(Datas) then error "Não existem datas nas fatos." else Date.StartOfYear(List.Min(Datas)),
    Fim = Date.EndOfYear(List.Max(Datas)),
    UltimoRealizado = List.Max(fLancamentos[competencia_data], null),
    Hoje = Date.From(DateTimeZone.SwitchZone(DateTimeZone.FixedUtcNow(), -3)),
    Dias = List.Dates(Inicio, Duration.Days(Fim-Inicio)+1, #duration(1,0,0,0)),
    Calendario = #table(
        type table [Data=date, Ano=Int64.Type, NomeMes=text, MesAbre=text, MesAno=text, MesNum=Int64.Type, AnoMesINT=Int64.Type, InicioMes=date, Trimestre=Int64.Type, TrimestreAbreviado=text, Bimestre=text, Semestre=text, Semana=Int64.Type, DiaSemana=Int64.Type, NomeDia=text, dataPassada=logical, AnoAtual=text, MesAtual=text],
        List.Transform(Dias, (d) => {
            d, Date.Year(d), Text.Proper(Date.MonthName(d,"pt-BR")),
            Text.Proper(Text.Start(Date.MonthName(d,"pt-BR"),3)),
            Text.Proper(Text.Start(Date.MonthName(d,"pt-BR"),3)) & "/" & Text.From(Date.Year(d)),
            Date.Month(d), Date.Year(d)*100+Date.Month(d), Date.StartOfMonth(d),
            Date.QuarterOfYear(d), Text.From(Date.QuarterOfYear(d)) & "º Trim",
            Text.From(Number.RoundUp(Date.Month(d)/2)) & "º Bim",
            Text.From(Number.RoundUp(Date.Month(d)/6)) & "º Sem",
            Date.WeekOfYear(d,Day.Monday), Date.DayOfWeek(d,Day.Monday)+1,
            Text.Proper(Date.DayOfWeekName(d,"pt-BR")),
            if UltimoRealizado = null then false else d <= Date.EndOfMonth(UltimoRealizado),
            if Date.Year(d)=Date.Year(Hoje) then "Ano Atual" else Text.From(Date.Year(d)),
            if Date.Year(d)=Date.Year(Hoje) and Date.Month(d)=Date.Month(Hoje) then "Mês Atual" else Text.Proper(Date.MonthName(d,"pt-BR"))
        })
    )
in
    Calendario
