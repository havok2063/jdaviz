<template>
  <j-tray-plugin
    :description="docs_description"
    :link="docs_link || 'https://jdaviz.readthedocs.io/en/'+vdocs+'/'+config+'/plugins.html#image-profiles-xy'"
    :uses_active_status="uses_active_status"
    @plugin-ping="plugin_ping($event)"
    :popout_button="popout_button"
    :scroll_to.sync="scroll_to">

    <plugin-viewer-select
      :items="viewer_items"
      :selected.sync="viewer_selected"
      label="Viewer"
      :show_if_single_entry="false"
      hint="Select a viewer to plot."
      persistent-hint
    />

    <v-row>
      <v-text-field
        v-model.number='selected_x'
        type="number"
        label="X"
        hint="Value of X"
      ></v-text-field>
    </v-row>

    <v-row>
      <v-text-field
        v-model.number='selected_y'
        type="number"
        label="Y"
        hint="Value of Y"
      ></v-text-field>
    </v-row>

    <v-row justify="end">
      <plugin-action-button
        :results_isolated_to_plugin="true"
        @click="draw_plot"
      >
        Plot
      </plugin-action-button>
    </v-row>

    <v-row v-if="plot_available">
      <jupyter-widget :widget="plot_across_x_widget"/>
      <br/>
      <jupyter-widget :widget="plot_across_y_widget"/>
    </v-row>

  </j-tray-plugin>
</template>
