<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:import href="xhtml/docbook.xsl"/>

  <xsl:param name="make.valid.html" select="1"/>

  <!--
  Print section label (number) along with the section, in the
  document body as well as in the toc.
  -->
  <xsl:param name="section.autolabel" select="1"/>

  <!--
  Up to heading6 in the toc
  -->
  <xsl:param name="toc.section.depth" select="6"/>
  <xsl:param name="toc.max.depth" select="8"/>

  <xsl:param name="suppress.navigation" select="1"/>

  <xsl:param name="spacing.paras" select="1"/>

  <!--
  Do not let DocBook XSL put style or hardcoded HTML "type" information on
  lists. We prefer to use the portal CSS.
  -->
  <xsl:param name="css.decoration" select="0"/>

  <xsl:param name="formal.title.placement">
    figure after
    example after
    equation after
    table after
    procedure after
    task after
  </xsl:param>

  <xsl:param name="generate.toc">
    appendix  toc,title
    article/appendix  nop
    article   toc,title
    book      toc,title,figure,table,example,equation
    chapter   toc,title
    part      toc,title
    preface   toc,title
    qandadiv  toc
    qandaset  toc
    reference toc,title
    sect1     toc
    sect2     toc
    sect3     toc
    sect4     toc
    sect5     toc
    section   toc
    set       toc,title
  </xsl:param>

</xsl:stylesheet>
